"""CodeRise: create a Windows icon from simple shapes."""
from pathlib import Path
from PIL import Image, ImageDraw


def make_icon(path: Path) -> None:
    size = 512
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, 500, 500), radius=114, fill="#101B2C")
    d.rounded_rectangle((25, 25, 487, 487), radius=100, outline="#335C7E", width=5)
    d.rounded_rectangle((96, 330, 187, 416), radius=16, fill="#3E7EAB")
    d.rounded_rectangle((207, 259, 298, 416), radius=16, fill="#56A4D2")
    d.rounded_rectangle((318, 176, 409, 416), radius=16, fill="#8ADBE4")
    d.line([(110, 265), (223, 174), (324, 98), (393, 98)], fill="#CCF4FC", width=18, joint="curve")
    d.polygon([(392, 68), (448, 98), (392, 128)], fill="#CCF4FC")
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32),
                                       (48, 48), (64, 64), (128, 128), (256, 256)])


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "build" / "coderise.ico"
    make_icon(target)
    print(f"Значок: {target}")
