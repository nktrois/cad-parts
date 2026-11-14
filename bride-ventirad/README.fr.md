# Bride de ventirad

*[English](README.md) · Français*

Barre qui passe dans la gorge de 14 mm du ventirad et s'accroche aux deux ergots du support de la carte mère pour plaquer le radiateur sur le processeur.

Faite pour une carte mère **ASRock FM2A88M Extreme4+ R2.0** (socket AMD FM2+). Les autres cartes qui ont les mêmes ergots de fixation AMD devraient convenir en ajustant les cotes ci-dessous.

## Impression

- PETG, couches de 0,2 mm, 5 périmètres, remplissage 100 %
- Le STL est déjà orienté sur chant, avec supports sous la barre

## Réglages

Tout se change en haut du `.scad` :

- `ecart` : distance entre les faces intérieures des deux boucles
- `appui` : hauteur entre le dessous des ergots et la surface d'appui sur le ventirad, c'est elle qui donne le serrage
- `fenetre_l`, `fenetre_h` : ouvertures pour les ergots
- `a_plat = true` pour voir la pièce en position de montage

Corriger les cotes dans la source plutôt que mettre à l'échelle dans le trancheur.

## État

Fonctionne sur mon montage. Le PETG peut se détendre avec le temps près d'un radiateur chaud : vérifier le serrage de temps en temps. Une lame ressort métallique reste plus fiable sur la durée.
