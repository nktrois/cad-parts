# Préparer les impressions

80 modèles originaux, chacun avec STL en millimètres, STEP et FCStd. Tous les encombrements STL sont inférieurs ou égaux à 235 mm sur chaque axe. Ils entrent individuellement dans le volume annoncé de 256 × 256 × 256 mm de la [Creator 5 Pro](https://eu.flashforge.com/products/flashforge-creator-5-pro). Le plateau FL10 fait 235 × 195 : il laisse 10,5 mm par côté sur l'axe de 235 si on le centre. Tenir compte de la bordure d'adhésion, des zones interdites et des contraintes du trancheur. Une station assemblée dépasse la hauteur d'une pièce et s'imprime en modules.

Les profils, temps et masses ne sont pas mesurés : aucun G-code n'est fourni. Le volume de matière du catalogue est celui du solide CAO ; il n'est pas une consommation de bobine déterminée par tranchage. À la publication initiale du 21 novembre 2026, les premières impressions restaient à réaliser. Les réglages seront actualisés à partir des retours d'impression.

## Ordre conseillé pour la filtration

| Étape | Pièces | Matière candidate | Présentation de départ au plateau |
|---|---|---|---|
| Ajustement | FL16 | TPU identifié | À plat, trous verticaux ; mesurer et tester la tige réelle |
| Joints | FL04, FL09 | Même TPU sélectionné | À plat ; contrôler l'épaisseur et les surfaces sans supports |
| Joint conique | FL05 | Même TPU sélectionné | Retourner pour poser la grande lèvre sur le plateau |
| Filtre | FL01 | PP sélectionné | Retourner pour poser la grande bride sur le plateau, tige vers le haut |
| Chambre et disques | FL02, FL03 **ou** FL17 | PP sélectionné | Bride/disques à plat ; vérifier l'ouverture des trous au tranchage |
| Récepteur | FL06 | PP sélectionné | Fond sur le plateau, ouverture en haut ; prévoir les supports extérieurs sous la bride débordante |
| Couvercle | FL07 ou FL08 | PP sélectionné | Face plate sur le plateau, embouts vers le haut |
| Bâti | FL10, FL11, FL12, FL13 | PETG, usage sec | Grandes faces planes au plateau ; inspecter les pontages des poches d'écrous |
| Accessoires | FL14, FL15 | PETG sec / PP selon contact | À plat, contrôler la reprise des ouvertures |

Les STL sont exportés avec le bas à z=0 pour l'inspection. Les orientations ci-dessus nécessitent de retourner FL01 et FL05 dans le trancheur. Elles sont des propositions à vérifier couche par couche. Les supports à l'intérieur d'un circuit mouillé compliquent le nettoyage et l'état de surface ; corriger la géométrie ou l'orientation si un profil en exige.

Pour le PP, utiliser les recommandations du fabricant du filament et une surface d'adhésion adaptée. Le retrait peut décaler les interfaces ; imprimer les essais avant les gros corps. Pour le TPU, sécher et régler selon sa référence exacte. Ni un remplissage à 100 %, ni une grande épaisseur de paroi ne prouvent l'étanchéité ou la résistance chimique.

Ne pas appliquer de revêtement ou de résine d'étanchéité sans sélectionner aussi sa compatibilité, son adhérence et son risque de contamination. Les joints doivent rester démontables et leurs portées accessibles au nettoyage.

## Autres séries

Les pièces d'atelier sèches sont candidates au PETG ; le PLA peut convenir à une maquette d'encombrement à température ambiante, sans lui attribuer une tenue en service chimique. Les béchers QB, cristallisoirs QC, entonnoirs QF/QP et outils humides ont le PP comme candidat, avec un choix de grade et des essais d'usage nécessaires. [Guide matériaux](recipients-chimiques/MATERIAUX.md).

## Modifier et régénérer

| Série | Où modifier les paramètres | Script à exécuter avec FreeCADCmd |
|---|---|---|
| Atelier, 45 pièces | `catalogue-base.json` | `scripts/build_freecad.py` |
| Récipients, 10 pièces | `SPECS` dans le générateur | `recipients-chimiques/scripts/build_recipients_freecad.py` |
| Outils humides, 8 pièces | `SPECS` dans le générateur | `outils-humides/scripts/build_freecad.py` |
| Filtration, 17 pièces | `P`, `SPECS` et générateurs associés | `filtration/scripts/build_system_freecad.py` |

Après les changements, régénérer les assemblages avec `scripts/build_assemblies_freecad.py` et `filtration/scripts/assemble_freecad.py`. Mettre à jour les positions si nécessaire. Exécuter ensuite avec Python `scripts/consolidate.py` et `scripts/validate_meshes.py` (NumPy), puis avec FreeCADCmd `scripts/validate_cad_freecad.py`. Les contrôles échouent si un modèle attendu est manquant ou invalide.

`scripts/render_blender.py` fonctionne avec Blender + NumPy, et `scripts/write_documentation.py` avec Python + Pillow. `scripts/check_package.py` vérifie les fichiers et liens locaux ; `scripts/package_library.py` produit l'archive sélectionnée dans le dossier de sortie passé en argument. Ces opérations restent locales et n'effectuent aucun push Git.
