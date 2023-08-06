from xml.sax.saxutils import escape
from .utils import *

class TextSetting:
    """Formatting for slices of a :class:`manim.mobject.svg.text_mobject.Text` object."""
    def __init__(
        self,
        start:int,
        end:int,
        font:str,
        slant,
        weight,
        line_num=-1
    ):
        self.start = start
        self.end = end
        self.font = font.encode('utf-8')
        self.slant = slant
        self.weight = weight
        self.line_num = line_num

def text2svg(
    settings:list,
    size:int,
    line_spacing:int,
    disable_liga:bool,
    file_name:str,
    START_X:int,
    START_Y:int,
    width:int,
    height:int,
    orig_text:str
) -> int:
    """Render an SVG file from a :class:`manim.mobject.svg.text_mobject.Text` object."""
    cdef cairo_surface_t* surface
    cdef cairo_t* cr
    cdef PangoFontDescription* font_desc
    cdef PangoLayout* layout
    cdef double width_layout = width
    cdef double font_size_c = size
    cdef cairo_status_t status
    cdef int temp_width

    file_name_bytes = file_name.encode("utf-8")
    surface = cairo_svg_surface_create(file_name_bytes,width,height)

    if surface == NULL:
        raise MemoryError("Cairo.SVGSurface can't be created.")

    cr = cairo_create(surface)
    status = cairo_status(cr)

    if cr == NULL or status == CAIRO_STATUS_NO_MEMORY:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise MemoryError("Cairo.Context can't be created.")
    elif status != CAIRO_STATUS_SUCCESS:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise Exception(cairo_status_to_string(status))

    cairo_move_to(cr,START_X,START_Y)
    offset_x = 0
    last_line_num = 0

    layout = pango_cairo_create_layout(cr)

    if layout==NULL:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise MemoryError("Pango.Layout can't be created from Cairo Context.")

    pango_layout_set_width(layout, pango_units_from_double(width_layout))
    for setting in settings:
        family = setting.font
        style = PangoUtils.str2style(setting.slant)
        weight = PangoUtils.str2weight(setting.weight)
        text_str = orig_text[setting.start : setting.end].replace("\n", " ")
        text = text_str.encode('utf-8')
        font_desc = pango_font_description_new()
        if font_desc==NULL:
            cairo_destroy(cr)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise MemoryError("Pango.FontDesc can't be created.")
        pango_font_description_set_size(font_desc, pango_units_from_double(font_size_c))
        if family:
            pango_font_description_set_family(font_desc, family)
        pango_font_description_set_style(font_desc, style.value)
        pango_font_description_set_weight(font_desc, weight.value)
        pango_layout_set_font_description(layout, font_desc)
        pango_font_description_free(font_desc)
        if setting.line_num != last_line_num:
            offset_x = 0
            last_line_num = setting.line_num
        cairo_move_to(cr,START_X + offset_x,START_Y + line_spacing * setting.line_num)

        pango_cairo_update_layout(cr,layout)
        if disable_liga:
            text_bytes = escape(text.decode('utf-8'))
            markup = f"<span font_features='liga=0,dlig=0,clig=0,hlig=0'>{text_bytes}</span>"
            markup_bytes = markup.encode('utf-8')
            pango_layout_set_markup(layout, markup_bytes, -1)
        else:
            pango_layout_set_text(layout,text,-1)
        pango_cairo_show_layout(cr, layout)
        pango_layout_get_size(layout,&temp_width,NULL)
        offset_x += pango_units_to_double(temp_width)

    status = cairo_status(cr)

    if cr == NULL or status == CAIRO_STATUS_NO_MEMORY:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        g_object_unref(layout)
        raise MemoryError("Cairo.Context can't be created.")
    elif status != CAIRO_STATUS_SUCCESS:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        g_object_unref(layout)
        raise Exception(cairo_status_to_string(status).decode())

    cairo_destroy(cr)
    cairo_surface_destroy(surface)
    g_object_unref(layout)
    return file_name

class MarkupUtils:
    @staticmethod
    def validate(text: str) -> bool:
        text_bytes = text.encode("utf-8")
        return pango_parse_markup(text_bytes, -1, 0, NULL, NULL, NULL, NULL)

    @staticmethod
    def text2svg(
        text: str,
        font: str,
        slant: str,
        weight: str,
        size: int,
        line_spacing: int,
        disable_liga: bool,
        file_name: str,
        START_X: int,
        START_Y: int,
        width: int,
        height: int,
    ) -> int:
        """Render an SVG file from a :class:`manim.mobject.svg.text_mobject.MarkupText` object."""
        cdef cairo_surface_t* surface
        cdef cairo_t* context
        cdef PangoFontDescription* font_desc
        cdef PangoLayout* layout
        cdef cairo_status_t status
        cdef double width_layout = width
        cdef double font_size = size

        file_name_bytes = file_name.encode("utf-8")

        if disable_liga:
            text_bytes = f"<span font_features='liga=0,dlig=0,clig=0,hlig=0'>{text}</span>".encode("utf-8")
        else:
            text_bytes = text.encode("utf-8")

        surface = cairo_svg_surface_create(file_name_bytes,width,height)
        if surface == NULL:
            raise MemoryError("Cairo.SVGSurface can't be created.")
        context = cairo_create(surface)
        status = cairo_status(context)
        if context == NULL or status == CAIRO_STATUS_NO_MEMORY:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            raise MemoryError("Cairo.Context can't be created.")
        elif status != CAIRO_STATUS_SUCCESS:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            raise Exception(cairo_status_to_string(status))

        cairo_move_to(context,START_X,START_Y)
        layout = pango_cairo_create_layout(context)
        if layout==NULL:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            raise MemoryError("Pango.Layout can't be created from Cairo Context.")
        pango_layout_set_width(layout, pango_units_from_double(width_layout))

        font_desc = pango_font_description_new()
        if font_desc==NULL:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise MemoryError("Pango.FontDesc can't be created.")
        pango_font_description_set_size(font_desc, pango_units_from_double(font_size))
        if font is not None and len(font) != 0:
            pango_font_description_set_family(font_desc, font.encode("utf-8"))
        pango_font_description_set_style(font_desc, PangoUtils.str2style(slant).value)
        pango_font_description_set_weight(font_desc, PangoUtils.str2weight(weight).value)
        pango_layout_set_font_description(layout, font_desc)
        pango_font_description_free(font_desc)

        cairo_move_to(context,START_X,START_Y)
        pango_cairo_update_layout(context,layout)
        pango_layout_set_markup(layout,text_bytes,-1)
        pango_cairo_show_layout(context, layout)

        status = cairo_status(context)
        if context == NULL or status == CAIRO_STATUS_NO_MEMORY:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise MemoryError("Cairo.Context can't be created.")
        elif status != CAIRO_STATUS_SUCCESS:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise Exception(cairo_status_to_string(status).decode())

        cairo_destroy(context)
        cairo_surface_destroy(surface)
        g_object_unref(layout)
        return file_name

cpdef str pango_version():
    return pango_version_string().decode('utf-8')

cpdef str cairo_version():
    return cairo_version_string().decode('utf-8')
