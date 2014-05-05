#include <ncurses.h>
#include <math.h>
 
//compila com
//cc ficheiro.c -lncurses -lm o2
 
 
typedef struct{
    int colorpair_no;
    int char_no;
}color_and_char;
 
color_and_char color4pixel(int x, int y, int cols, int rows, int time);
 
 
void generate_all_color_pairs() {
    int foreground;
    int background;
    int i = 1;
    for (background = 0; background < 8; background++) {
        for (foreground = 0; foreground < 8; foreground++) {
            init_pair(i, foreground, background);
            i++;
        }
    }
}
 
int main() {
 
    int t = 0;
    initscr();
    cbreak(); /* Start curses mode 		  */
 
    start_color();
 
    generate_all_color_pairs();
 
    for (;;) {
        int x, y;
        move(0, 0);
        for (y = 0; y < LINES; y++) {
            for (x = 0; x < COLS; x++) {
                color_and_char c_a_c = color4pixel(x, y, COLS, LINES, t);
 
                attron(COLOR_PAIR(c_a_c.colorpair_no));
                addch(55 + c_a_c.char_no);
            }
        }
        refresh();
        t++;
    }
    getch();
    endwin();
    return 0;
}
 
int distance(int alin, int acol, int blin, int bcol) {
    int dy = alin - blin;
    int dx = acol - bcol;
    return (int) sqrt(dx * dx + dy * dy);
}
 
color_and_char color4pixel(int x, int y, int cols, int rows, int t) {
    int xx = (cols / 3) * sin((float) (t + x + y) / 60.0);
    int yy = (rows / 3) * cos((float) (t + y * 2) / 43.0);
 
    int distance_to_center = distance(y + yy, x + xx, rows / 2, cols / 2);
 
    distance_to_center >>= 2;
    //distance_to_center <<=1;
    distance_to_center &= 15;
	color_and_char cac;
	cac.colorpair_no = distance_to_center;
	cac.char_no = distance_to_center;
    return cac;
}
