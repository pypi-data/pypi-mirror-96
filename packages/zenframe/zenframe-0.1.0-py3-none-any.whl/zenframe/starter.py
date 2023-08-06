from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
import argparse
import traceback
import sys
import json
import time

import zenframe.util
from zenframe.finisher import terminate_all_subprocess, invoke_destructors, setup_interrupt_handlers
from zenframe.unbound import unbound_worker_top_half, start_unbounded_worker

from zenframe.configuration import Configuration
from zenframe.retransler import ConsoleRetransler
from zenframe.communicator import Communicator


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__()

        #self.add_argument("--zenframe", action="store_true", help="Test frame sublibrary")
        self.add_argument("--unbound", action="store_true")
        self.add_argument("--display", action="store_true")
        self.add_argument("--frame", action="store_true")
        self.add_argument("--prescale", action="store_true")
        self.add_argument("--sleeped", action="store_true",
                          help="Don't use manualy. Create sleeped thread.")
        self.add_argument("--size")
        self.add_argument("paths", type=str, nargs="*", help="runned file")
        self.add_argument("--no-restore", action="store_true")

    def parse_args(self, *args, **kwargs):
        pargs = super().parse_args(*args, **kwargs)

        if Configuration.TRACE_EXEC_OPTION:
            from zenframe.util import print_to_stderr
            print_to_stderr(sys.argv, pargs)

        return pargs


def protect_path(s):
    if s[0] == s[-1] and (s[0] == "'" or s[0] == '"'):
        return s[1:-1]
    return s


def invoke(pargs, frame_creator, exec_top_half, exec_bottom_half):
    setup_interrupt_handlers()

    try:
        # Удаляем кавычки из пути, если он есть
        if len(pargs.paths) > 0:
            pargs.paths[0] = protect_path(pargs.paths[0])

        if pargs.display:
            exec_worker_only(pargs)

        elif pargs.unbound:
            exec_worker_unbound(pargs, exec_top_half, exec_bottom_half)

        else:
            exec_frame_process(pargs, frame_creator)

    except Exception as ex:
        from zenframe.util import print_to_stderr
        print_to_stderr(f"Finished with exception", ex)
        print_to_stderr(f"Exception class: {ex.__class__}")
        traceback.print_exc()

    invoke_destructors()
    terminate_all_subprocess()


def exec_frame_process(pargs, frame_creator):
    """ Запускает графическую оболочку, которая управляет.
            Потоками с виджетами отображения. """

    openpath = pargs.paths[0] if len(pargs.paths) > 0 else None

    zenframe.util.set_debug_process_name("MAIN")
    start_application(
        frame_creator,
        openpath=openpath,
        unbound=pargs.frame,
        norestore=pargs.no_restore)


def exec_worker_only(pargs):
    """ Режим запускает один единственный виджет.
        Простой режим, никакой ретрансляции команд, никаких биндов. """

    if len(pargs.paths) != 1:
        raise Exception("Display mode invoked without path")

    runpy.run_path(pargs.paths[0], run_name="__main__")


def exec_worker_unbound(pargs, top_half, bottom_half):
    """ Запускает виджет отображения, зависимый от графической
            оболочки."""

    unbound_worker_top_half(
        top_half=top_half,
        bottom_half=bottom_half)


def start_application(frame_creator, openpath=None, unbound=False, norestore=False):
    QAPP = QtWidgets.QApplication(sys.argv[1:])
    initial_communicator = None

    if unbound:
        # Переопределяем дескрипторы, чтобы стандартный поток вывода пошёл
        # через ретранслятор. Теперь все консольные сообщения будуут обвешиваться
        # тегами и поступать на коммуникатор.
        retransler = ConsoleRetransler(sys.stdout)
        retransler.start_listen()

        # Коммуникатор будет слать сообщения на скрытый файл,
        # тоесть, на истинный stdout
        initial_communicator = Communicator(
            ifile=sys.stdin, ofile=retransler.new_file)

        # Показываем ретранслятору его коммуникатор.
        retransler.set_communicator(initial_communicator)

        data = initial_communicator.simple_read()
        dct0 = json.loads(data)

        initial_communicator.declared_opposite_pid = int(dct0["data"])

    MAINWINDOW, openpath = frame_creator(
        openpath, initial_communicator, norestore, unbound)

    if unbound:
        initial_communicator.bind_handler(MAINWINDOW.new_worker_message)
        initial_communicator.start_listen()

        MAINWINDOW.set_retransler(retransler)

    if openpath:
        if not unbound:
            MAINWINDOW.open(openpath)
        else:
            MAINWINDOW.open_declared(openpath)

    timer = QtCore.QTimer()
    timer.start(Configuration.TIMER_PULSE * 1000)
    timer.timeout.connect(lambda: None)

    MAINWINDOW.show()
    QAPP.exec()
