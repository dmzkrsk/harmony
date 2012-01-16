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

def getAttr(element, attribute, required, validator, default=None):
    """
    Доступ к аттрибуту с проверками

    :type element: xml.dom.minidom.Element
    :type attribute: str or unicode
    :type validator: Callable
    :type required: bool
    """

    if not element.hasAttribute(attribute) and not required:
        return default

    if not element.hasAttribute(attribute) and required:
        raise ParseException(u'Элемент %s должен содержать элемент %s' % (element.tagName, attribute))

    return validator(element.getAttribute(attribute))
