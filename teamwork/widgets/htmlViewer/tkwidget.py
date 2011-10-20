## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##


# imports
import os, sys, re, string, types, Tkinter
import traceback

# PySol imports
from mfxutil import destruct, kwdefault, KwStruct
from mfxutil import win32api

# Toolkit imports
from tkconst import tkversion
from tkconst import EVENT_HANDLED, EVENT_PROPAGATE
from tkutil import getFont
from tkutil import after, after_idle, after_cancel
from tkutil import bind, unbind_destroy, makeImage
from tkutil import makeToplevel, setTransient


# /***********************************************************************
# // abstract base class for the dialogs in this module
# ************************************************************************/

class _ToplevelDialog:
    img = None
    def __init__(self, parent, title="", resizable=0, default=-1):
        self.parent = parent
        self.status = 0
        self.button = default
        self.timer = None
        self.top = makeToplevel(parent, title=title)
        self.top.wm_resizable(resizable, resizable)
        bind(self.top, "WM_DELETE_WINDOW", self.wmDeleteWindow)
        if self.img is None:
            _ToplevelDialog.img = (makeImage(dither=0, data="""
R0lGODlhIAAgAPICAH8AAH9/f7+/v/8AAP///wAAAAAAAAAAACH5BAEAAAIALAAAAAAgACAAAAPZ
KLos8PC1SRccOGNYO9AgCHTNE57ZQwoA6mZAB7z0AFRA/QLBBISEFyEECDAAIYISpSSEAAwAqKkM
UQkgQGABCF011xAgEBAAUFfMFQUICACu69UFCAgAL7nyBSADaHI0AGQANHI0AGQAL3oELwBkAC6N
Si4AZAAoVxhXKABkAgAhVxpXIQBkAQIAIFchVyAAqQIAIU0oTSEAZAsAIQQvBCEAqQwAOi4AqQEM
AMgoAKkTAM8gAKkVD9UPyx0BAMgAywErARAoEOMrC2QREeMB6w3w9AHyFfUrCQA7"""),
makeImage(dither=0, data="""
R0lGODlhIAAgAPIDAAAAAAAA/39/f7+/v////wAAAAAAAAAAACH5BAEAAAMALAAAAAAgACAAAAPU
OLo88vC1SRccJOsBa32DJo7D4zHCMK7jIJyDwA5BHQws4AksYds9AEXQI/xqRUBDMCgOfoPiAMAQ
FK8sgEAhGGC/mgFAMBBcjzUsQDAQfI9YAOR7xAIg3yMWAPkesQAQA1hHVwMADwMCWEdXABADAgNX
R0UDABAKAj1oNiwAEAwAYEUAEQ0ApCsAERQAA6oEAwARHgAAA18DtxEwArcAAysDwBECMAoQwAMa
AMYPyAwRABoAxtEVAgAaAA/YyAAZAA/fyAAEAA/lyLcP68gQ78gPMAkAOw=="""),
makeImage(dither=0, data="""
R0lGODlhIAAgAPIDAAAAAAAA/39/f7+/v////wAAAAAAAAAAACH5BAEAAAMALAAAAAAgACAAAAPp
OLo88vC1SRccJOsBa32DJo7D4zHCMK7jIJyDwM4j4AnsEOz8wAIUAWsQGGR4gQEL0BAMWDsRkjUA
MAQzZAY5AwgUgsEMSRggZwOAYCCgDXYDApJGAAgGArpmwNMDIHoZPIEAEIEEOwOBABCHO4cAEAOH
hwMADwMCegM7A3oAEAMCA3RIdAMAEAoCdEh0ABAMADQDOwM0ABENAJQrABEUAAO9BAMAER4AAAOB
A8oRMALKAAMrA9MRAjAKENMDGgDZD9sMEQAaANnkFQIAGgAP69sAGQAP8tsABAAP+NvKD/xtgyBw
2wMYCQAAOw=="""), makeImage(dither=0, data="""
R0lGODlhIAAgAPIDAAAAAH9/AH9/f7+/v///AAAAAAAAAAAAACH5BAEAAAMALAAAAAAgACAAAAPu
OLq88S3KqQIhA9Atw70DIHDkEHwXIAglFaDXAKytFMAXsNZNgF8DwIq3CPwugBVxEDheBoAVMfAZ
AK6DD2DFC6Cu4M8AsKoFUOArCrBqBWBpAGoAWJUCsDgMsCIFcHEwAwArHAE4AWABOAArGwE/A2AD
OAMAKxQBR2BHACsTAU4BAAFHAwArEgFOAwADTgArEQFOFwC1AwArDQG1vhcAKwwBvgNXA04DACsL
Ab5ptQArCgG/abUDACsDAb8DVwO+ACsDAb/nFwArAgHovwMA6wMB7k4DAOsCCgFx/f79+QQwCEiw
oEEBEQ4qJKggAQA7"""))

    def mainloop(self, focus=None, timeout=0):
        bind(self.top, "<Escape>", self.mCancel)
        if focus is not None:
            focus.focus()
        setTransient(self.top, self.parent)
        try:
            self.top.grab_set()
        except Tkinter.TclError:
            pass
        if timeout > 0:
            self.timer = after(self.top, timeout, self.mTimeout)
        try: self.top.mainloop()
        except SystemExit: pass
        self.destroy()

    def destroy(self):
        after_cancel(self.timer)
        unbind_destroy(self.top)
        try:
            self.top.wm_withdraw()
        except:
            if traceback: traceback.print_exc()
            pass
        try:
            self.top.destroy()
        except:
            if traceback: traceback.print_exc()
            pass
        destruct(self.top)
        if self.parent:
            try:
                ##self.parent.update_idletasks()
                # FIXME: why do we need this under Windows ?
                if hasattr(self.parent, "busyUpdate"):
                    self.parent.busyUpdate()
                else:
                    self.parent.update()
            except:
                if traceback: traceback.print_exc()
                pass
        self.top = None
        self.parent = None

    def getDefaultFont(self):
        return getFont("default")

    def wmDeleteWindow(self, *event):
        self.status = 1
        raise SystemExit
        ##return EVENT_HANDLED

    def mCancel(self, *event):
        self.status = 1
        raise SystemExit

    def mTimeout(self, *event):
        self.status = 2
        raise SystemExit


# /***********************************************************************
# // replacement for the tk_dialog script
# ************************************************************************/

class MfxDialog(_ToplevelDialog):
    def __init__(self, parent, title, **kw):
        kw = self.initKw(kw)
        _ToplevelDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.button = kw.default
        msg = Tkinter.Label(top_frame, text=kw.text, justify=kw.justify,
                            width=kw.width, font=kw.font)
        msg.pack(fill=Tkinter.BOTH, expand=1, padx=kw.padx, pady=kw.pady)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
            timeout=0, resizable=0,
            text="", justify="center",
            strings=("OK",), default=0,
            width=0,
            font=self.getDefaultFont(),
            buttonfont=self.getDefaultFont(),
            padx=20, pady=20,
            bitmap=None, bitmap_side="left", bitmap_padx=10, bitmap_pady=20,
            image=None, image_side="left", image_padx=10, image_pady=20,
        )
        # default to separator if more than one button
        sw = 2 * (len(kw.strings) > 1)
        kwdefault(kw.__dict__, separatorwidth=sw)
        return kw

    def createFrames(self, kw):
        bottom_frame = Tkinter.Frame(self.top)
        bottom_frame.pack(side=Tkinter.BOTTOM, fill=Tkinter.BOTH, ipady=3)
        if kw.separatorwidth > 0:
            separator = Tkinter.Frame(self.top, relief="sunken",
                    height=kw.separatorwidth, width=kw.separatorwidth,
                    borderwidth=kw.separatorwidth / 2)
            separator.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        top_frame = Tkinter.Frame(self.top)
        top_frame.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        return top_frame, bottom_frame

    def createBitmaps(self, frame, kw):
        bm = ["error", "info", "questhead", "warning"]
        if kw.bitmap in bm:
            b = Tkinter.Label(frame, image=self.img[bm.index(kw.bitmap)])
            b.pack(side=kw.bitmap_side, padx=kw.bitmap_padx, pady=kw.bitmap_pady)
        elif kw.bitmap:
            b = Tkinter.Label(frame, bitmap=kw.bitmap)
            b.pack(side=kw.bitmap_side, padx=kw.bitmap_padx, pady=kw.bitmap_pady)
        elif kw.image:
            b = Tkinter.Label(frame, image=kw.image)
            b.pack(side=kw.image_side, padx=kw.image_padx, pady=kw.image_pady)

    def createButtons(self, frame, kw):
        button = column = -1
        padx, pady = kw.get("buttonpadx", 10), kw.get("buttonpady", 10)
        focus = None
        max_len = 6
        for s in kw.strings:
            if type(s) is types.TupleType:
                s = s[0]
            if s:
                s = re.sub(r"[\s\.\,]", "", s)
                max_len = max(max_len, len(s))
        for s in kw.strings:
            xbutton = button = button + 1
            if type(s) is types.TupleType:
                assert len(s) == 2
                button = int(s[1])
                s = s[0]
            if s is None:
                continue
            if button < 0:
                b = Tkinter.Button(frame, text=s, font=kw.buttonfont, state="disabled")
                button = xbutton
            else:
                b = Tkinter.Button(frame, text=s, font=kw.buttonfont, default="normal",
                                   command=(lambda self=self, button=button: self.mDone(button)))
                if button == kw.default:
                    focus = b
                    focus.config(default="active")
            l = len(s)
            if 1 and l < max_len:
                l = l + (max_len - l) / 2
                b.config(width=l)
            column = column + 1
            b.grid_configure(column=column, row=0, sticky="ew", padx=padx, pady=pady)
            b.grid_columnconfigure(column)
        if focus is not None:
            l = (lambda event=None, self=self, button=kw.default: self.mDone(button))
            bind(self.top, "<Return>", l)
            bind(self.top, "<KP_Enter>", l)
        return focus

    def mDone(self, button):
        self.button = button
        raise SystemExit


# /***********************************************************************
# //
# ************************************************************************/

class MfxExceptionDialog(MfxDialog):
    def __init__(self, parent, ex, title="Error", **kw):
        kw = KwStruct(kw, bitmap="error")
        text = str(kw.get("text", ""))
        if text and text[-1] != "\n":
            text = text + "\n"
        text = text + "\n"
        if isinstance(ex, EnvironmentError) and ex.filename is not None:
            t = "[Errno %s] %s:\n%s" % (ex.errno, ex.strerror, repr(ex.filename))
        else:
            t = str(ex)
        kw.text = text + t
        apply(MfxDialog.__init__, (self, parent, title), kw.getKw())


# /***********************************************************************
# //
# ************************************************************************/

class MfxSimpleSlider(MfxDialog):
    def __init__(self, parent, title,
                 label, value, from_, to, resolution, **kw):
        kw = self.initKw(kw)
        _ToplevelDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.value = value
        self.var = Tkinter.DoubleVar()
        self.var.set(value)
        slider = Tkinter.Scale(top_frame, from_=from_, to=to,
                               resolution=resolution, orient=Tkinter.HORIZONTAL,
                               length="3i", label=label, variable=self.var, takefocus=0)
        slider.pack(side=Tkinter.TOP, padx=kw.padx, pady=kw.pady)
        #
        focus = self.createButtons(bottom_frame, kw)
        self.mainloop(focus, kw.timeout)

    def initKw(self, kw):
        kw = KwStruct(kw,
            strings=("OK", "Cancel"), default=0,
            separatorwidth = 0,
        )
        return MfxDialog.initKw(self, kw)

    def mDone(self, button):
        self.button = button
        self.value = self.var.get()
        raise SystemExit


# /***********************************************************************
# //
# ************************************************************************/

class MfxSimpleEntry(MfxSimpleSlider):
    def __init__(self, parent, title, label, value, **kw):
        kw = self.initKw(kw)
        _ToplevelDialog.__init__(self, parent, title, kw.resizable, kw.default)
        top_frame, bottom_frame = self.createFrames(kw)
        self.createBitmaps(top_frame, kw)
        #
        self.value = value
        if label:
            label = Tkinter.Label(top_frame, text=label, takefocus=0)
            label.pack(pady=5)
        w = kw.get("e_width", 0)    # width in characters
        self.var = Tkinter.Entry(top_frame, exportselection=1, width=w)
        self.var.insert(0, value)
        self.var.pack(side=Tkinter.TOP, padx=kw.padx, pady=kw.pady)
        #
        focus = self.createButtons(bottom_frame, kw)
        focus = self.var
        self.mainloop(focus, kw.timeout)


# /***********************************************************************
# // a simple tooltip
# ************************************************************************/

class MfxTooltip:
    def __init__(self, widget):
        # private vars
        self.widget = widget
        self.text = None
        self.timer = None
        self.tooltip = None
        self.label = None
        self.bindings = []
        self.bindings.append(self.widget.bind("<Enter>", self._enter))
        self.bindings.append(self.widget.bind("<Leave>", self._leave))
        self.bindings.append(self.widget.bind("<ButtonPress>", self._leave))
        # user overrideable settings
        self.time = 1000                    # milliseconds
        self.relief = Tkinter.SOLID
        self.justify = Tkinter.LEFT
        self.fg = "#000000"
        self.bg = "#ffffe0"
        self.xoffset = 20
        self.yoffset = 1

    def setText(self, text):
        self.text = text

    def _unbind(self):
        if self.bindings and self.widget:
            self.widget.unbind("<Enter>", self.bindings[0])
            self.widget.unbind("<Leave>", self.bindings[1])
            self.widget.unbind("<ButtonPress>", self.bindings[2])
            self.bindings = []

    def destroy(self):
        self._unbind()
        self._leave()

    def _enter(self, *event):
        after_cancel(self.timer)
        self.timer = after(self.widget, self.time, self._showTip)

    def _leave(self, *event):
        after_cancel(self.timer)
        self.timer = None
        if self.tooltip:
            self.label.destroy()
            destruct(self.label)
            self.label = None
            self.tooltip.destroy()
            destruct(self.tooltip)
            self.tooltip = None

    def _showTip(self):
        if self.tooltip or not self.text:
            return
        c = self.widget.__class__
        if c in (Tkinter.Button,):
            if self.widget["state"] == Tkinter.DISABLED:
                return
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        x = x + self.xoffset
        y = y + self.yoffset
        self.tooltip = Tkinter.Toplevel()
        self.tooltip.wm_iconify()
        self.tooltip.wm_overrideredirect(1)
        self.tooltip.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.label = Tkinter.Label(self.tooltip, text=self.text,
                         relief=self.relief, justify=self.justify,
                         fg=self.fg, bg=self.bg, bd=1, takefocus=0)
        self.label.pack(ipadx=1, ipady=1)
        self.tooltip.wm_geometry("%+d%+d" % (x, y))
        self.tooltip.wm_deiconify()
        ##self.tooltip.tkraise()


# /***********************************************************************
# // A canvas widget with scrollbars and some useful bindings.
# ************************************************************************/

class MfxScrolledCanvas:
    def __init__(self, parent, hbar=2, vbar=2, **kw):
        bg = kw.get("bg", parent.cget("bg"))
        kwdefault(kw, bg=bg, highlightthickness=0,
                  xscrollincrement=16, yscrollincrement=16)
        self.parent = parent
        self.createFrame(kw)
        self.canvas = None
        self.hbar = None
        self.hbar_mode = hbar
        self.vbar = None
        self.vbar_mode = vbar
        self.hbar_show = 0
        self.vbar_show = 0
        self.resize_pending = 0
        self.timer = None
        self.createCanvas(kw)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        if hbar:
            if hbar == 3:
                w = 21
                if win32api:
                    w = win32api.GetSystemMetrics(3)        # SM_CYHSCROLL
                self.frame.grid_rowconfigure(1, minsize=w)
            self.createHbar(bg)
            if not vbar:
                bind(self.hbar, "<Map>", self._mapBar)
            self.bindHbar()
        if vbar:
            if vbar == 3:
                w = 21
                if win32api:
                    w = win32api.GetSystemMetrics(2)        # SM_CXVSCROLL
                self.frame.grid_columnconfigure(1, minsize=w)
            self.createVbar(bg)
            bind(self.vbar, "<Map>", self._mapBar)
            self.bindVbar()
        ###self.canvas.focus_set()

    #
    #
    #

    def destroy(self):
        after_cancel(self.timer)
        self.timer = None
        self.unbind_all()
        self.canvas.destroy()
        self.frame.destroy()

    def pack(self, **kw):
        apply(self.frame.pack, (), kw)

    #
    #
    #

    def unbind_all(self):
        unbind_destroy(self.hbar)
        unbind_destroy(self.vbar)
        unbind_destroy(self.canvas)
        unbind_destroy(self.frame)

    def createFrame(self, kw):
        width = kw.get("width")
        height = kw.get("height")
        self.frame = Tkinter.Frame(self.parent, width=width, height=height, bg=None)
    def createCanvas(self, kw):
        self.canvas = apply(Tkinter.Canvas, (self.frame,), kw)
        self.canvas.grid(row=0, column=0, sticky="news")
    def createHbar(self, bg):
        self.hbar = Tkinter.Scrollbar(self.frame, name="hbar", bg=bg, takefocus=0, orient="horizontal")
        self.canvas["xscrollcommand"] = self._setHbar
        self.hbar["command"] = self.canvas.xview
    def createVbar(self, bg):
        self.vbar = Tkinter.Scrollbar(self.frame, name="vbar", bg=bg, takefocus=0)
        self.canvas["yscrollcommand"] = self._setVbar
        self.vbar["command"] = self.canvas.yview
    def bindHbar(self, w=None):
        if w is None:
            w = self.canvas
        bind(w, "<KeyPress-Left>", self.unit_left)
        bind(w, "<KeyPress-Right>", self.unit_right)
    def bindVbar(self, w=None):
        if w is None:
            w = self.canvas
        bind(w, "<KeyPress-Prior>", self.page_up)
        bind(w, "<KeyPress-Next>", self.page_down)
        bind(w, "<KeyPress-Up>", self.unit_up)
        bind(w, "<KeyPress-Down>", self.unit_down)
        bind(w, "<KeyPress-Begin>", self.scroll_top)
        bind(w, "<KeyPress-Home>", self.scroll_top)
        bind(w, "<KeyPress-End>", self.scroll_bottom)

    def _mapBar(self, event):
        # see: autoscroll.tcl, http://mini.net/cgi-bin/wikit/950.html
        top = event.widget.winfo_toplevel()
        g = top.wm_geometry()
        if self.resize_pending:
            self.resize_pending = 0
            self.canvas.update_idletasks()
        top.wm_geometry(g)

    def _setHbar(self, *args):
        apply(self.hbar.set, args)
        self.showHbar()
    def _setVbar(self, *args):
        apply(self.vbar.set, args)
        self.showVbar()

    def showHbar(self, show=-1):
        if not self.hbar:
            return 0
        if show < 0:
            show = self.hbar_mode
        if show > 1:
            if not self.canvas.winfo_ismapped():
                return 0
            view = self.canvas.xview()
            show = abs(view[0]) > 0.0001 or abs(view[1] - 1.0) > 0.0001
        if show == self.hbar_show:
            return 0
        if show:
            self.hbar.grid(row=1, column=0, sticky="we")
        else:
            self.hbar.grid_forget()
        self.hbar_show = show
        return 1

    def showVbar(self, show=-1):
        if not self.vbar:
            return 0
        if show < 0:
            show = self.vbar_mode
        if show > 1:
            if not self.canvas.winfo_ismapped():
                return 0
            view = self.canvas.yview()
            show = abs(view[0]) > 0.0001 or abs(view[1] - 1.0) > 0.0001
        if show == self.vbar_show:
            return 0
        if show:
            self.vbar.grid(row=0, column=1, sticky="ns")
        else:
            self.vbar.grid_forget()
        self.vbar_show = show
        return 1

    def page_up(self, *event):
        self.canvas.yview_scroll(-1, "page")
        return "break"
    def page_down(self, *event):
        self.canvas.yview_scroll(1, "page")
        return "break"
    def unit_up(self, *event):
        self.canvas.yview_scroll(-1, "unit")
        return "break"
    def unit_down(self, *event):
        self.canvas.yview_scroll(1, "unit")
        return "break"
    def page_left(self, *event):
        self.canvas.xview_scroll(-1, "page")
        return "break"
    def page_right(self, *event):
        self.canvas.xview_scroll(1, "page")
        return "break"
    def unit_left(self, *event):
        self.canvas.xview_scroll(-1, "unit")
        return "break"
    def unit_right(self, *event):
        self.canvas.xview_scroll(1, "unit")
        return "break"
    def scroll_top(self, *event):
        self.canvas.yview_moveto(0)
        return "break"
    def scroll_bottom(self, *event):
        self.canvas.yview_moveto(1)
        return "break"


# /***********************************************************************
# //
# ************************************************************************/


def tkwidget_main(args):
    from tkutil import wm_withdraw
    tk = Tkinter.Tk()
    wm_withdraw(tk)
    tk.update()
    if 1:
        d = MfxDialog(tk, "title", text="This is an info dialog",
                      bitmap="info", default=0, strings=("OK",))
        print d.status, d.button
    if 1:
        d = MfxSimpleSlider(tk, "title", "label", 1.0, 0.2, 9.9, 0.1)
        print d.status, d.value
    if 1:
        d = MfxSimpleEntry(tk, "title", "label", "value")
        print d.status, d.value
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(tkwidget_main(sys.argv))

