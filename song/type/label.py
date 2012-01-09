# coding=utf-8
from lib.timed import Timed, TimedSheet

class Label(Timed):
    """
    Класс метки

    Кроме времени начала у метки есть цвет и текст
    """
    def __init__(self, title, start, color):
        """
        :type title: str or unicode
        :type start: float
        :type color: str or unicode or RandomColor
        """
        super(Label, self).__init__(start)
        self.title = title
        self.color = color

    def isEmpty(self):
        """
        Метка пуста, если у нее нет текста

        :rtype: bool
        """
        return not self.title

class LabelSheet(TimedSheet):
    """
    Коллекция меток
    """
    def _append(self, label):
        """
        Специфичная для класса реализация добавления объекта

        Реализует умное добавление меток: идущие подряд одинаковые метки (имеющие одинаковый цвет и текст "склеиваются"

        :param label: Label
        :rtype: None
        """
        assert isinstance(label, Label), label.__class__

        if self.listOfTimed:
            # Достаем последнюю метку в списке
            last = self.listOfTimed[-1]
            # Если метки совпадают. то просто не добавляем их. "Скелются" они автоматически в iterTimed
            if last.title == label.title and last.color == label.color:
                return

        self.listOfTimed.append(label)
