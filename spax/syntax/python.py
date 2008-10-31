
import keyword

TAB_WIDTH = 4
TAB_TO_SPACE = True

styles = {
	'keyword': ("|".join(["(%s)" % kw for kw in keyword.kwlist]), {'bold': True})
}
