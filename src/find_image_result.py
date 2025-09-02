from attrs import define


@define(frozen=True)
class FindImageResult:
    val: float
    coords: tuple[int, int]  # top-left corner of match
    template_w: int          # width of matched template
    template_h: int          # height of matched template
