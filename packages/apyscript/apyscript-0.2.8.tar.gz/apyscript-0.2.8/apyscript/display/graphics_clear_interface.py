"""Class implementation for graphics clear method related interface.
"""


from typing import List
from typing import Optional

from apyscript.display.display_object import DisplayObject
from apyscript.type.number import Number


class GraphicsClearInterface:

    _fill_color: Optional[str] = None
    _fill_alpha: Number = Number(1.0)
    _line_color: Optional[str] = None
    _line_thickness: Optional[int] = None
    _line_alpha: Optional[float] = None
    _childs: List[DisplayObject]

    def clear(self) -> None:
        """
        Clear all graphics and reset fill and line settings.
        """
        self._fill_color = None
        self._fill_alpha = Number(1.0)
        self._line_color = None
        self._line_thickness = None
        self._line_alpha = None
        while self._childs:
            self._childs[0].remove_from_parent()
