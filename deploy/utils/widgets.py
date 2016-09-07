def sanitize_line_edit(text, allow_point, line_edit):
    """
    Removes non-numerical symbols
    :param text: String. Current contents of a line edit
    :param allow_point: Boolean. Whether it is an integer or float
    :param line_edit: PyQt4.QtGui.LineEdit.
    :return: None
    """
    if len(text) > 0 and not text[-1].isdigit():
        if not allow_point or text[-1] != '.' or text.count('.') > 1:
            line_edit.setText(line_edit.text()[:-1])
