ecart = 98;
barre_l = 13.4;
barre_ep = 4;
boucle_l = 21;
boucle_ep = 4;
fenetre_l = 14;
fenetre_h = 6;
semelle = 3;
appui = 10;
a_plat = false;

$fn = 32;

z_barre = semelle + appui;
h = z_barre + barre_ep;

module fenetre() {
    rotate([0, 90, 0])
        linear_extrude(boucle_ep + 2, center = true)
            offset(r = 0.7)
                square([fenetre_h - 1.4, fenetre_l - 1.4], center = true);
}

module bride() {
    difference() {
        union() {
            translate([-ecart/2, -barre_l/2, z_barre])
                cube([ecart, barre_l, barre_ep]);
            for (s = [-1, 1]) {
                x = s * (ecart/2 + boucle_ep/2);
                translate([x, 0, h/2])
                    cube([boucle_ep, boucle_l, h], center = true);
                hull() {
                    translate([s * (ecart/2 - 9), 0, z_barre + barre_ep/2])
                        cube([1, barre_l, barre_ep], center = true);
                    translate([x, 0, z_barre + barre_ep/2])
                        cube([boucle_ep, boucle_l, barre_ep], center = true);
                }
            }
        }
        for (s = [-1, 1])
            translate([s * (ecart/2 + boucle_ep/2), 0, semelle + fenetre_h/2])
                fenetre();
    }
}

if (a_plat)
    bride();
else
    translate([0, 0, boucle_l/2]) rotate([90, 0, 0]) bride();
