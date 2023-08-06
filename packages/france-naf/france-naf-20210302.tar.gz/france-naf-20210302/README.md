# france-naf

Python accessors to NAF/APE codes.

From https://www.insee.fr/fr/information/2406147

## Installation

    pip install france-naf


## Usage

    from naf import DB

    # Get one NAF object
    my_naf = DB["02.30Z"]
    print(my_naf)

    # "Récolte de produits forestiers non ligneux poussant à l'état sauvage"
    "02.30Z" in DB
    # True
    print(my_naf.section) or print(my_naf.section.code)
    # 'A'
    print(my_naf.section.description)
    # 'AGRICULTURE, SYLVICULTURE ET PÊCHE'

    dict(my_naf)
    # {'code': '02.30Z',
    # 'description': "Récolte de produits forestiers non ligneux poussant à l'état sauvage",
    # 'classe': {'code': '02.30',
    #  'description': "Récolte de produits forestiers non ligneux poussant à l'état sauvage"},
    # 'groupe': {'code': '02.3',
    #  'description': "Récolte de produits forestiers non ligneux poussant à l'état sauvage"},
    # 'division': {'code': '02',
    #  'description': 'Sylviculture et exploitation forestière'},
    # 'section': {'code': 'A', 'description': 'AGRICULTURE, SYLVICULTURE ET PÊCHE'}}

    # Iter over NAF objects
    for naf in DB:
        do_something_with(naf)
    # Iter over code, description
    for code, description in DB.pairs():
        pass
    # Get the whole DB as a json string
    str(DB)
