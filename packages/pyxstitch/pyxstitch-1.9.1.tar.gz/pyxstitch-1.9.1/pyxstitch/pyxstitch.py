#!/usr/bin/python3
"""App for pyxstitch."""
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_all_styles
import pyxstitch.formatter as fmt
import pyxstitch.output as out_fmt
import pyxstitch.font as fnt
import pyxstitch.version as vers
import pyxstitch.log as log
import pyxstitch.utils as utils
import argparse
import os
import sys
from pathlib import Path

_PNG = "png"
_RAW = out_fmt.RAW_FORMAT
_DEF_STYLE = "monokai"
_PDF = "pdf"
_TXT = ".txt"
_AUTODETECT = "autodetect"
_LIGHT = "light"
_DARK = "dark"
_DMC = "-dmc"
_LIGHT_DMC = _LIGHT + _DMC
_DARK_DMC = _DARK + _DMC
_B_AND_W = "bw"
_BANNER = 35
_BANNER_ONE = [17, 21, 25, 32]
_BANNER_TWO = [0, 1, 4, 6, 8, 10, 13, 14, 17, 25, 29, 30, 32]
_BANNER_THREE = [0, 2, 4, 6, 9, 13, 16, 17, 18, 21, 24, 25, 26, 28, 32, 33, 34]
_BANNER_FOUR = [0, 1, 5, 6, 8, 10, 12, 13, 17, 20, 21, 22, 25, 29, 30, 32, 34]
_BANNER_FIVE = [0, 6]
_BANNER_SIX = [0, 4, 5]


class InputArgs(object):
    """Input argumentss."""

    def __init__(self, args):
        """Init the input args."""
        for attr in dir(args):
            if attr.startswith("_"):
                continue
            setattr(self, attr, getattr(args, attr))
        self.is_raw = args.format == _RAW
        self.is_light = args.theme == _LIGHT
        self.default_style = args.style == _DEF_STYLE
        self.is_text = args.file == _TXT
        self.is_dark = args.theme.startswith(_DARK)
        self.is_dmc = args.theme.endswith(_DMC)
        self.invalid = False
        self._max = sys.maxsize
        self.hzoom = self._zoom("horizontal", args.hszoom, args.hezoom)
        self.vzoom = self._zoom("vertical", args.vszoom, args.vezoom)

    def _zoom(self, zoom_type, start, end):
        """Get zoom tuple for start/end."""
        u_start = 0
        u_end = self._max
        if start > 0:
            u_start = start
        if end > 0:
            u_end = end
        error_msg = None
        if start < 0 or end < 0:
            error_msg = "< 0"
        elif end < start:
            error_msg = "end < start"
        if error_msg:
            log.Log.write("invalid {} zoom request ({})".format(zoom_type,
                                                                error_msg))
            self.invalid = True
        return (u_start, u_end)


def _create_file_name(file_name, args):
    """Create output file names."""
    return "{}.{}".format(file_name, args.format)


def _print_spacer():
    """Print a spacer line."""
    _print_banner_line(range(0, _BANNER),
                       character='=',
                       leading="=",
                       trailing="=")


def _print_banner_line(marks, character='X', leading=" ", trailing=""):
    """Print a banner line."""
    actual = []
    for i in range(0, _BANNER):
        char = ' '
        if i in marks:
            char = character
        actual.append(char)
    log.Log.write(leading + "".join(actual) + trailing)


def _print_banner():
    """Print the pyxstitch banner."""
    _print_spacer()
    _print_banner_line(_BANNER_ONE)
    _print_banner_line(_BANNER_TWO)
    _print_banner_line(_BANNER_THREE)
    _print_banner_line(_BANNER_FOUR)
    _print_banner_line(_BANNER_FIVE)
    _print_banner_line(_BANNER_SIX)
    _print_spacer()


def _replay(args, file_name, content):
    """Do replay."""
    if args.is_raw:
        log.Log.write("can not replay raw to raw")
        exit(1)
    if not args.is_light or not args.default_style:
        log.Log.write('style and theme ignored during replay')
    out = args.output
    if args.output is None:
        out = _create_file_name(file_name, args)
    playback = out_fmt.TextFormat()
    playback.replay(content, out)
    exit(0)


def main():
    """Main-entry point."""
    utils.supported()
    default_font = fnt.Font().detect
    parser = argparse.ArgumentParser(
            description='Convert source code files to cross stitch patterns.')
    parser.add_argument('--file', help="""input source code file to create a
pattern from.""", type=str, default=_TXT)
    parser.add_argument('--lexer', help="""the source code lexer to use when
reading input and converting input tokens into colors""", type=str)
    parser.add_argument('--output', help="""output name""", type=str)
    parser.add_argument('--theme',
                        help="""pattern theme. indicates the background and
symbol color outputs for the output pattern""",
                        type=str,
                        default=_LIGHT,
                        choices=[_B_AND_W,
                                 _DARK,
                                 _DARK_DMC,
                                 _LIGHT,
                                 _LIGHT_DMC])
    parser.add_argument('--kv', metavar='N', help="""key/value configuration
parameters for setting the output format""", type=str, nargs='+')
    parser.add_argument('--map', help="""when selecting colors will map one
token color to another color (override)""", metavar='N', type=str, nargs='+')
    parser.add_argument('--config', help="""configuration file""", type=str)
    parser.add_argument('--multipage', help="""enable multipage output""",
                        type=str,
                        default=out_fmt.MULTI_PAGE_AUTO,
                        choices=[out_fmt.MULTI_PAGE_AUTO,
                                 out_fmt.MULTI_PAGE_OFF,
                                 out_fmt.MULTI_PAGE_ON])
    parser.add_argument('--format',
                        help="""output file format""",
                        type=str,
                        default=_PNG,
                        choices=["jpg", _PDF, _PNG, _RAW])
    parser.add_argument('--style',
                        help="""token color styling (from pygments)""",
                        default=_DEF_STYLE,
                        choices=list(sorted(get_all_styles())))
    font_choices = list(sorted(list(fnt.get_all_fonts()) + [default_font]))
    parser.add_argument('--font',
                        help="""font to use for the pattern""",
                        default=default_font,
                        choices=font_choices)
    parser.add_argument('--version',
                        action="store_true",
                        help="""display version""")
    parser.add_argument('--quiet',
                        action="store_true",
                        help="""less verbose output""")
    parser.add_argument('--symbols',
                        type=str,
                        help="""symbol set for stitching symbols""")
    parser.add_argument('--hszoom',
                        type=int,
                        default=0,
                        help="horizontal start zoom")
    parser.add_argument('--hezoom',
                        type=int,
                        default=0,
                        help="horizontal end zoom")
    parser.add_argument('--vszoom', type=int, default=0,
                        help="vertical start zoom")
    parser.add_argument('--vezoom', type=int, default=0,
                        help="vertical end zoom")
    args = parser.parse_args()
    if args.version:
        if not args.quiet:
            log.Log.writeln()
            _print_banner()
        log.Log.write(vers.__version__)
        if not args.quiet:
            log.Log.writeln()
        exit(0)
    if args.quiet:
        log.Log.is_verbose = False
    inputs = InputArgs(args)
    if inputs.invalid:
        exit(1)
    _run(inputs, default_font)


def _run(args, default_font):
    """Run pyxstitch."""
    content = None
    file_name = None
    file_ext = os.path.splitext(args.file)
    is_raw = False
    for item in file_ext:
        if item == "." + _RAW:
            is_raw = True
            break
    default_lexer = get_lexer_by_name("text")
    use_lexer = args.lexer
    use_style = args.style
    is_bw = False
    # Shortcut to black and white is to just use a Text lexer
    if args.theme == _B_AND_W:
        if use_lexer is not None:
            log.Log.write("black & white overrides lexer input")
        if use_style != _DEF_STYLE:
            log.Log.write("black & white overrides style")
        use_lexer = "Text"
        use_style = _B_AND_W
        is_bw = True
    is_auto = use_lexer == _AUTODETECT
    if is_auto:
        use_lexer = None
    if not is_raw:
        if use_lexer or args.is_text:
            if use_lexer:
                lexer = get_lexer_by_name(use_lexer)
            else:
                lexer = default_lexer
        else:
            try:
                lexer = get_lexer_for_filename(args.file)
            except Exception as e:
                log.Log.write(e)
                exit(1)
    if os.path.exists(args.file):
        file_name = file_ext[0]
        with open(args.file, 'r') as f:
            content = f.read()
    else:
        if file_ext[1] is not None and len(file_ext[1]) > 1:
            log.Log.write("file not found, pass extension for stdin or a file")
            exit(1)
        file_name = "output"
        content = "".join(sys.stdin.readlines())
    if is_raw:
        _replay(args, file_name, content)
    if is_auto:
        log.Log.write(content)
        try:
            lexer = guess_lexer(content)
            log.Log.write('using {} lexer'.format(lexer.name))
        except Exception as e:
            log.Log.write('unable to guess a lexer...defaulting to text')
            lexer = default_lexer
    output_name = args.output
    is_raw = args.is_raw
    if output_name is None:
        output_name = _create_file_name(file_name, args)
    else:
        if args.output.endswith(_RAW) and not is_raw:
            log.Log.write('specify output as {}?'.format(_RAW))
            exit(1)
    preproc = fnt.preprocess(content)
    text = preproc[0]
    rows = preproc[1]
    cols = preproc[2]
    config_file = args.config
    if config_file is None:
        home = utils.home()
        conf = os.path.join(home, ".pyxstitch.config")
        if os.path.exists(conf):
            config_file = conf
    if config_file is not None and not os.path.exists(config_file):
        log.Log.write("unable to find config file: {}".format(config_file))
    formatting = fmt.new_formatter(use_style,
                                   output_name,
                                   args.multipage,
                                   colorize=args.is_dmc,
                                   dark=args.is_dark,
                                   is_raw=is_raw,
                                   is_bw=is_bw,
                                   map_colors=args.map,
                                   font_name=args.font,
                                   rows=rows,
                                   columns=cols,
                                   symbols=args.symbols,
                                   config=args.kv,
                                   config_file=config_file,
                                   horizontal=args.hzoom,
                                   vertical=args.vzoom)
    if args.font == default_font:
        log.Log.write("font: {}".format(formatting.font_factory.display_name))
    log.Log.write("Using lexer: {}".format(lexer.name))
    highlight(text, lexer, formatting)


if __name__ == '__main__':
    main()
