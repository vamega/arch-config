from prompt_toolkit.layout import FormattedTextControl
from prompt_toolkit.mouse_events import MouseEventType


class Separator:
    line = "-" * 15

    def __init__(self, line=None):
        if line:
            self.line = line

    def __str__(self):
        return self.line


def if_mousedown(handler):
    def handle_if_mouse_down(mouse_event):
        if mouse_event.event_type == MouseEventType.MOUSE_DOWN:
            return handler(mouse_event)
        else:
            return NotImplemented

    return handle_if_mouse_down


class InquirerControl(FormattedTextControl):
    def __init__(self, choices, pointer_index, **kwargs):
        self.pointer_index = pointer_index
        self.pointer_sign = kwargs.pop("pointer_sign", "\u276f")
        self.selected_sign = kwargs.pop("selected_sign", "\u25cf")
        self.unselected_sign = kwargs.pop("unselected_sign", "\u25cb")
        self.selected_options = []  # list of names
        self.answered = False
        self.answered_correctly = True
        self.error_message = None
        self._init_choices(choices)
        super().__init__(self._get_choice_tokens, **kwargs)

    def _init_choices(self, choices):
        # helper to convert from question format to internal format
        self.choices = []  # list (name, value)
        searching_first_choice = True if self.pointer_index == 0 else False
        for i, c in enumerate(choices):
            if isinstance(c, Separator):
                self.choices.append(c)
            else:
                name = c["name"]
                value = c.get("value", name)
                disabled = c.get("disabled")
                description = c.get("description", None)
                if c.get("checked") and not disabled:
                    self.selected_options.append(value)
                self.choices.append((name, value, disabled, description))
                if (
                    searching_first_choice and not disabled
                ):  # find the first (available) choice
                    self.pointer_index = i
                    searching_first_choice = False

    @property
    def choice_count(self):
        return len(self.choices)

    def _get_choice_tokens(self):
        tokens = []

        def append(index, line):
            if isinstance(line, Separator):
                tokens.append(("class:Separator", "  %s\n" % line))
            else:
                line_name = line[0]
                line_value = line[1]
                selected = (
                    line_value in self.selected_options
                )  # use value to check if option has been selected
                pointed_at = index == self.pointer_index

                @if_mousedown
                def select_item(mouse_event):
                    # bind option with this index to mouse event
                    if line_value in self.selected_options:
                        self.selected_options.remove(line_value)
                    else:
                        self.selected_options.append(line_value)

                if pointed_at:
                    tokens.append(
                        ("class:pointer", " {}".format(self.pointer_sign), select_item)
                    )  # ' >'
                else:
                    tokens.append(("", "  ", select_item))
                # 'o ' - FISHEYE
                if choice[2]:  # disabled
                    tokens.append(("", "- %s (%s)" % (choice[0], choice[2])))
                else:
                    if selected:
                        tokens.append(
                            (
                                "class:selected",
                                "{} ".format(self.selected_sign),
                                select_item,
                            )
                        )
                    else:
                        tokens.append(
                            ("", "{} ".format(self.unselected_sign), select_item)
                        )

                    if pointed_at:
                        tokens.append(("[SetCursorPosition]", ""))

                    if choice[3]:  # description
                        tokens.append(("", "%s - %s" % (line_name, choice[3])))
                    else:
                        tokens.append(("", line_name, select_item))
                tokens.append(("", "\n"))

        # prepare the select choices
        for i, choice in enumerate(self.choices):
            append(i, choice)
        tokens.pop()  # Remove last newline.
        return tokens

    def get_selected_values(self):
        # get values not labels
        return [
            c[1]
            for c in self.choices
            if not isinstance(c, Separator) and c[1] in self.selected_options
        ]

    @property
    def line_count(self):
        return len(self.choices)
