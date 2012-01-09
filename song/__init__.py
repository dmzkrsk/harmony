# coding=utf-8
class ParseException(Exception):
    """
    Ошибка разбора XML
    """
    pass

def iterElements(node):
    """
    Итератор по DOM-элементу

    Возвращает только другие элементы

    :type node: xml.dom.minidom.Element
    :rtype: iterator(xml.dom.minidom.Element)
    """
    return (x for x in node.childNodes if x.nodeType == x.ELEMENT_NODE)
