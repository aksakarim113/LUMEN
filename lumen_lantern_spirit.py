from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math, random

W, H = 720, 720
PATTERNS = [(1, 2), (2, 3), (3, 4), (1, 1), (3, 2), (1, 3)]
pat, O1, O2, amp = 1, math.pi / 2, 0.6, 170          # Lissajous settings
cx, cy = W / 2, H / 2 - 20                            # centre of the curve
u, ox, oy = 0.0, cx, cy                               # time on curve, spirit position
mode, paused, tick = 'title', False, 0
score, best, energy, hit, shake = 0, 0, 100.0, 0, 0
trail, wisps, thorns, ripples, petals = [], [], [], [], []
CYAN, GOLD, PINK = (0.4, 0.9, 1.0), (1.0, 0.9, 0.4), (0.8, 0.1, 0.6)
F12, F18, F24 = GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24
flies = [(random.uniform(0, W), random.uniform(0, H), random.uniform(0, 6.28),
          random.uniform(0.01, 0.03)) for _ in range(40)]


def place(x, y, rot=0, sx=1, sy=None):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(rot, 0, 0, 1)
    glScalef(sx, sx if sy is None else sy, 1)


def disc(x, y, r, seg=36):
    place(x, y, 0, r)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(seg + 1):
        glVertex2f(math.cos(2 * math.pi * i / seg), math.sin(2 * math.pi * i / seg))
    glEnd()
    glPopMatrix()


def glow(x, y, r, col, a):
    
    place(x, y, 0, r)
    glBegin(GL_TRIANGLE_FAN)
    glColor4f(*col, a)
    glVertex2f(0, 0)
    glColor4f(*col, 0)
    for i in range(37):
        glVertex2f(math.cos(2 * math.pi * i / 36), math.sin(2 * math.pi * i / 36))
    glEnd()
    glPopMatrix()


def star(x, y, r, rot, n, inner):
    place(x, y, rot, r)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(2 * n + 1):
        k = 1 if i % 2 == 0 else inner
        glVertex2f(k * math.cos(math.pi / 2 + i * math.pi / n), k * math.sin(math.pi / 2 + i * math.pi / n))
    glEnd()
    glPopMatrix()


def ring(x, y, r):
    glBegin(GL_LINE_STRIP)
    for i in range(49):
        glVertex2f(x + r * math.cos(2 * math.pi * i / 48), y + r * math.sin(2 * math.pi * i / 48))
    glEnd()


def rect(x0, y0, x1, y1):
    glBegin(GL_QUADS)
    for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        glVertex2f(*p)
    glEnd()


def text(x, y, s, font=F18):
    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(font, ord(ch))


def dist(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


# ---------------------------------------------------------------- curve
def curve_point(t):
    a, b = PATTERNS[pat]
    return cx + amp * math.sin(a * t + O1), cy + amp * math.cos(b * t + O2)


def clamp_center():
    global cx, cy, amp
    amp = max(90, min(290, amp))
    cx = max(amp + 30, min(W - amp - 30, cx))
    cy = max(amp + 30, min(H - amp - 70, cy))


# ---------------------------------------------------------------- scenery
def petal(w, h, col):
    glColor4f(*col)
    glBegin(GL_TRIANGLES)
    glVertex2f(-w, 0)
    glVertex2f(w, 0)
    glVertex2f(0, h)
    glEnd()


def lotus(x, y, s):
    sway = 3 * math.sin(tick * 0.03 + x)
    
    for angles, sw, w, h, col in (((14, 42, 70), sway, 10, 42, (0.75, 0.25, 0.55, 0.85)),
                                  ((0, 28, 56), -sway, 8, 30, (1.0, 0.6, 0.8, 0.9))):
        for a in angles:
            for mirror in ((1, -1) if a else (1,)):      
                place(x, y, sw, mirror * s, s)
                glRotatef(a, 0, 0, 1)
                petal(w, h, col)
                glPopMatrix()
    glColor3f(1.0, 0.85, 0.3)
    disc(x, y + 3 * s, 5 * s)


def background():
    glBegin(GL_QUADS)                                    # sky -> water gradient
    glColor3f(0.02, 0.12, 0.18); glVertex2f(0, 0); glVertex2f(W, 0)
    glColor3f(0.06, 0.02, 0.17); glVertex2f(W, H); glVertex2f(0, H)
    glEnd()
    glow(W * 0.78, H * 0.78, 130, (0.7, 0.9, 1.0), 0.2)  # moon
    glColor4f(0.85, 0.95, 1.0, 0.25)
    disc(W * 0.78, H * 0.78, 40)
    for bx, by, ph, sp in flies:                         # drifting fireflies
        a = 0.2 + 0.3 * math.sin(tick * 0.05 + ph)
        x, y = bx + 30 * math.sin(tick * sp + ph), by + 20 * math.cos(tick * sp * 1.3 + ph)
        glow(x, y, 6, (0.8, 1.0, 0.6), a * 0.8)
        glColor4f(1.0, 1.0, 0.8, a)
        disc(x, y, 1.8, 8)
    for x, y, r in ((250, 55, 38), (W - 240, 95, 30), (70, 300, 26), (W - 60, 360, 28)):
        y += 2 * math.sin(tick * 0.03 + x)               # lily pads bob on the water
        glColor4f(0.05, 0.35, 0.25, 0.8); disc(x, y, r)
        glColor4f(0.1, 0.5, 0.35, 0.6); disc(x, y, r * 0.6)
    lotus(95, 70, 1.0)
    lotus(W - 105, 55, 0.8)
    lotus(W - 40, 480, 0.55)



def draw_curve():
    glColor4f(*CYAN, 0.28)
    glBegin(GL_LINE_STRIP)
    for i in range(212):
        glVertex2f(*curve_point(i * 0.03))
    glEnd()
    glColor4f(*CYAN, 0.5)
    disc(cx, cy, 3, 10)


def draw_trail():
    for i, (x, y) in enumerate(trail):
        f = (i + 1) / len(trail)
        glColor4f(0.5, 0.95, 1.0, 0.35 * f)
        disc(x, y, 3 + 9 * f, 14)


def draw_orb():
    glow(ox, oy, 46, (1.0, 0.3, 0.3) if hit else CYAN, 0.3)
    glColor3f(1.0, 0.5, 0.5) if hit and (tick // 3) % 2 == 0 else glColor3f(0.85, 1.0, 1.0)
    disc(ox, oy, 12)
    glColor3f(1, 1, 1)
    disc(ox, oy, 6)
    glColor4f(1, 1, 1, 0.8)
    star(ox, oy, 22, tick * 3, 4, 0.2)


def draw_wisp(w):
    x, y, ph, life = w
    fade = min(1.0, life / 90.0)
    p = 0.5 + 0.5 * math.sin(tick * 0.12 + ph)
    glow(x, y, 30 + 4 * p, GOLD, (0.28 + 0.08 * p) * fade)
    glColor4f(1.0, 0.85, 0.3, fade)
    star(x, y, 14, -tick * 2 + ph * 50, 4, 0.3)
    glColor4f(1.0, 1.0, 0.8, fade)
    star(x, y, 6, -tick * 2 + ph * 50, 4, 0.5)


def draw_thorn(t):
    x, y, _, _, ph = t
    p = 0.5 + 0.5 * math.sin(tick * 0.15 + ph)
    glow(x, y, 40, PINK, 0.2 + 0.15 * p)
    place(x, y, tick * 1.5 + ph * 40)
    glColor3f(0.22, 0.05, 0.28)
    for _ in range(7):                                  
        glBegin(GL_TRIANGLES)
        glVertex2f(18 * math.cos(0.3), -18 * math.sin(0.3))
        glVertex2f(18 * math.cos(0.3), 18 * math.sin(0.3))
        glVertex2f(34, 0)
        glEnd()
        glRotatef(360 / 7, 0, 0, 1)
    glColor3f(0.1, 0.02, 0.15); disc(0, 0, 19)
    glColor3f(1.0, 0.2 + 0.4 * p, 0.7); disc(0, 0, 6)
    glPopMatrix()


def draw_effects():
    for x, y, r, mx, *col in ripples:                    # expanding rings
        for k in range(3):
            glColor4f(*col, max(0.0, 1 - r / mx) * 0.55)
            ring(x, y, r + k * 1.5)
    for x, y, _, _, life, rot, _, *col in petals:        
        place(x, y, rot)
        glColor4f(*col, max(life, 0))
        glBegin(GL_QUADS)
        for p in ((0, -9), (5, 0), (0, 9), (-5, 0)):
            glVertex2f(*p)
        glEnd()
        glPopMatrix()


def draw_hud():
    glColor3f(1, 1, 1); text(20, H - 38, "LIGHT: %d" % score)
    glColor3f(0.6, 0.85, 1.0); text(20, H - 58, "BEST: %d" % best, F12)
    glColor3f(0.7, 0.95, 1.0); text(W - 140, H - 38, "CURVE  %d : %d" % PATTERNS[pat], F12)
    x0, x1, y0, y1 = 170, W - 170, H - 42, H - 26
    glColor4f(0, 0, 0, 0.5)
    rect(x0 - 3, y0 - 3, x1 + 3, y1 + 3)
    low = energy < 25 and (tick // 8) % 2 == 0
    c1, c2 = ((1, .2, .2), (1, .3, .3)) if low else ((1, .8, .2), (.4, 1, .9))
    fill = x0 + (x1 - x0) * max(energy, 0) / 100
    glBegin(GL_QUADS)                                    # smooth colour across the bar
    glColor3f(*c1); glVertex2f(x0, y0)
    glColor3f(*c2); glVertex2f(fill, y0); glVertex2f(fill, y1)
    glColor3f(*c1); glVertex2f(x0, y1)
    glEnd()


def overlay(alpha, lines):
    glColor4f(0, 0.02, 0.06, alpha)
    rect(0, 0, W, H)
    y = H / 2 + 110
    for s, font, col, off in lines:
        glColor3f(*col)
        text(W / 2 - off, y, s, font)
        y -= 34

# ---------------------------------------------------------------- game logic
def start_game():
    global mode, paused, score, energy, hit, shake
    mode, paused, score, energy, hit, shake = 'play', False, 0, 100.0, 0, 0
    for lst in (wisps, thorns, ripples, petals):
        del lst[:]


def burst(x, y, r, g, b, n=12):
    for _ in range(n):
        a, sp = random.uniform(0, 6.28), random.uniform(1, 4.5)
        petals.append([x, y, sp * math.cos(a), sp * math.sin(a), 1.0,
                       random.uniform(0, 360), random.uniform(-8, 8), r, g, b])

def pulse():
    global energy
    if mode != 'play' or paused or energy < 15:
        return
    energy -= 12
    ripples.append([ox, oy, 10, 230, 0.6, 0.9, 1.0])
    for t in thorns[:]:
        if dist(ox, oy, t[0], t[1]) < 210:
            burst(t[0], t[1], 0.8, 0.2, 0.7, 14)
            thorns.remove(t)

def update_game():
    global energy, score, hit, shake, mode, best
    energy -= 0.035 + min(score * 0.0015, 0.05)
    hit = max(0, hit - 1)
    while len(wisps) < 3:
        wisps.append([random.uniform(70, W - 70), random.uniform(70, H - 110),
                      random.uniform(0, 6.28), random.randint(500, 800)])
    for w in wisps[:]:
        w[3] -= 1
        if w[3] <= 0:
            wisps.remove(w)
        elif dist(ox, oy, w[0], w[1]) < 32:
            score += 1
            energy = min(100.0, energy + 20)
            ripples.append([w[0], w[1], 8, 120, 1.0, 0.9, 0.4])
            burst(w[0], w[1], 1.0, 0.7, 0.85)
            wisps.remove(w)
    while len(thorns) < min(1 + score // 3, 6):
        for _ in range(20):                             
            x, y = random.uniform(40, W - 40), random.uniform(40, H - 90)
            if dist(x, y, ox, oy) > 250:
                break
        a, sp = random.uniform(0, 6.28), random.uniform(0.8, 1.6) + min(score * 0.03, 1.2)
        thorns.append([x, y, sp * math.cos(a), sp * math.sin(a), random.uniform(0, 6.28)])
    for t in thorns:
        t[0] += t[2]
        t[1] += t[3]
        if not 30 < t[0] < W - 30:
            t[2] = -t[2]
        if not 30 < t[1] < H - 80:
            t[3] = -t[3]
        if hit == 0 and dist(ox, oy, t[0], t[1]) < 34:
            energy, hit, shake = energy - 25, 60, 14
            burst(ox, oy, 1.0, 0.3, 0.3, 14)
    if energy <= 0:
        energy, best, mode = 0, max(best, score), 'over'


def update(_):
    global tick, u, ox, oy, shake
    tick += 1
    shake = max(0, shake - 1)
    if not paused:
        u += 0.022
        ox, oy = curve_point(u)
        trail.append((ox, oy))
        del trail[:-40]
        if mode == 'play':
            update_game()
        for r in ripples[:]:
            r[2] += 3.5
            if r[2] >= r[3]:
                ripples.remove(r)
        for p in petals[:]:
            p[0] += p[2]; p[1] += p[3]; p[3] -= 0.04; p[4] -= 0.02; p[5] += p[6]
            if p[4] <= 0:
                petals.remove(p)
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


# ---------------------------------------------------------------- input
def arrowkey(key, x, y):
    global O2, amp
    if key == GLUT_KEY_RIGHT: O2 += 0.15
    elif key == GLUT_KEY_LEFT: O2 -= 0.15
    elif key == GLUT_KEY_UP: amp += 15
    elif key == GLUT_KEY_DOWN: amp -= 15
    clamp_center()


def normalkey(key, x, y):
    global pat, paused
    if key == b'd': pat = (pat + 1) % len(PATTERNS)
    elif key == b'a': pat = (pat - 1) % len(PATTERNS)
    elif key == b' ': start_game() if mode == 'title' else pulse()
    elif key == b'p': paused = not paused
    elif key == b'r': start_game()
    elif key == b'\x1b': exit()


def mouseclick(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        mousedrag(x, y)
        if mode == 'title':
            start_game()


def mousedrag(x, y):
    global cx, cy
    cx, cy = x, H - y
    clamp_center()


# ---------------------------------------------------------------- display
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT)
    glViewport(0, 0, W, H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if shake:                                            # screen shake = random translation
        glTranslatef(random.uniform(-shake, shake) * 0.4, random.uniform(-shake, shake) * 0.4, 0)

    background()
    draw_curve()
    for w in wisps: draw_wisp(w)
    for t in thorns: draw_thorn(t)
    draw_trail()
    draw_orb()
    draw_effects()
    draw_hud()
    if mode == 'title':
        W_, C = (1, 1, 1), (0.8, 0.9, 1)
        overlay(0.55, [("L U M E N", F24, (0.6, 1, 1), 50),
                       ("The Lantern Spirit of the Lotus Pond", F18, W_, 150), ("", F12, W_, 0),
                       ("Shape the curve so the spirit touches the golden wisps.", F12, C, 150),
                       ("Arrows: twist & resize     A / D: change pattern", F12, C, 140),
                       ("Mouse: move the curve      SPACE: light pulse", F12, C, 135), ("", F12, W_, 0),
                       ("Press SPACE or click to begin", F18, (1, 0.85, 0.4), 120)])
    elif mode == 'over':
        overlay(0.65, [("THE LIGHT FADES...", F24, (1, 0.5, 0.6), 100),
                       ("You gathered %d wisps" % score, F18, (1, 1, 1), 85),
                       ("Press R to try again", F18, (1, 0.85, 0.4), 85)])
    elif paused:
        overlay(0.5, [("PAUSED", F24, (1, 1, 1), 45)])
    glutSwapBuffers()

clamp_center()
glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(W, H)
glutInitWindowPosition(250, 40)
glutCreateWindow(b"LUMEN - Lantern Spirit")
glEnable(GL_BLEND)                                       
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glShadeModel(GL_SMOOTH)                                  
glutDisplayFunc(showScreen)
glutSpecialFunc(arrowkey)
glutKeyboardFunc(normalkey)
glutMouseFunc(mouseclick)
glutMotionFunc(mousedrag)
glutTimerFunc(16, update, 0)
glutMainLoop()