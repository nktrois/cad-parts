# Matériaux : chimie, température et capacité de la machine

L'objectif de cette série est le contact avec des produits chimiques. La sélection exige le réactif, sa concentration, la température, la durée, la charge mécanique, le grade commercial et le procédé. Ni le nom du polymère, ni un pH, ni une température de buse ne déterminent seuls une température de service chimique.

| Famille | Intérêt et limite pour cette série |
|---|---|
| PP non chargé | Première matière candidate pour de nombreuses solutions aqueuses acides ou basiques compatibles. Vérifier le grade et les conditions exactes ; attention notamment aux agents fortement oxydants. Surface et profil d'impression spécifiques nécessaires. |
| PA6-CF / PAHT-CF | Intérêt principalement mécanique/thermique ; un polyamide renforcé ne devient pas un contenant universel pour acides. |
| PC | Utile pour certains besoins mécaniques et thermiques ; résistance limitée à de nombreux agents, en particulier aux bases. |
| PPS-CF | Candidat intéressant combinant résistance chimique et thermique, à sélectionner et qualifier pour le produit réel. Ni la charge carbone ni une HDT élevée ne prouvent l'étanchéité ou la propreté d'un contenant. |
| PEEK | Large résistance chimique et thermique selon le grade et le réactif, mais hors capacités d'impression de la Creator 5 Pro standard. |

[Comparatif chimique des polymères — Ensinger](https://www.ensingerplastics.com/en-gb/plastic-material-selection/chemical-resistant). Les données génériques de polymères ne sont pas une homologation de ces STL.

## Exemple PPS-CF10 et Creator 5 Pro

Polymaker préconise pour Fiberon PPS-CF10 une buse à **310–350 °C**, un plateau à **80–90 °C** et une buse résistante à l'abrasion. La Creator 5 Pro est limitée à **320 °C** : elle ne couvre que le bas de la plage. L'adhésion inter-couches et les propriétés réelles doivent être qualifiées à la température disponible.

Les éprouvettes de la fiche PPS-CF10 sont imprimées à 330–350 °C puis recuites à 125 °C pendant 16 h. Les valeurs HDT de 252,5 °C à 0,45 MPa et 133 °C à 1,8 MPa ne constituent pas des températures de service d'un bécher, encore moins en présence d'un réactif. Un éventuel recuit peut aussi modifier les dimensions ; il nécessite un équipement adapté et ne remplace pas les essais d'usage.

[Fiche technique Polymaker](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PPS-CF10_V1.1_EN-1.pdf) ; [limites constructeur Creator 5 Pro](https://eu.flashforge.com/products/flashforge-creator-5-pro).

## Pourquoi pas du PEEK sur cette machine ?

Les exigences exactes dépendent du grade. À titre d'exemple, 3DXTECH indique 375–410 °C à la buse pour le PEEK dans sa FAQ, au-delà des 320 °C de la machine ; le plateau et l'enceinte ont aussi des exigences plus élevées. Acheter une bobine ne rend pas la machine compatible.

[Exigences d'impression — 3DXTECH](https://www.3dxtech.com/pages/frequently-asked-questions) ; [résistance chimique PEEK — Victrex](https://www.victrex.com/-/media/downloads/technical-guides/victrex_chemical_resistance_en_us.pdf?rev=f76d9f3e32854c24b98ad32b2353bc4d).

## Récipients PP chauffés

La température de fusion ou d'autoclave d'un produit moulé n'autorise pas le chauffage direct d'une impression. Thermo Fisher précise que ses béchers Nalgene ne sont pas destinés à la plaque chauffante. Les modèles de ce dépôt n'ont donc aucune qualification de chauffe.

[Béchers de laboratoire — Thermo Fisher](https://www.thermofisher.com/py/en/home/life-science/lab-plasticware-supplies/reusable-plasticware/plastic-beakers.html) ; [fiche d'un filament PP — Forward AM](https://forward-am.com/wp-content/uploads/2021/07/Ultrafuse_PP_TDS_EN_v4.0.pdf) ; [étude de compatibilité de pièces FFF](https://research.aalto.fi/en/publications/chemical-compatibility-of-fused-filament-fabrication-based-3-d-pr/).
