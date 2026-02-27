"""
Tea Flavor & Aroma Wheel Taxonomy
Based on World Tea Flavor Wheel + SCA Flavor Wheel adaptation for tea.
"""

FLAVOR_WHEEL = {
    "Floral": {
        "color": "#FFB3C6",
        "subcategories": {
            "Rose": ["rose", "розовый", "роза", "rosewater", "rosehip"],
            "Jasmine": ["jasmine", "жасмин", "jasminum"],
            "Orchid": ["orchid", "орхидея"],
            "Chrysanthemum": ["chrysanthemum", "хризантема", "mum"],
            "Lilac": ["lilac", "сирень", "lilacs"],
            "Lavender": ["lavender", "лаванда"],
            "Osmanthus": ["osmanthus", "османтус", "sweet olive"],
            "Magnolia": ["magnolia", "магнолия"],
            "Honeysuckle": ["honeysuckle", "жимолость"],
            "Lotus": ["lotus", "лотос"],
            "Violet": ["violet", "фиалка"],
            "Floral (general)": ["floral", "цветочный", "flower", "blooms", "blossom", "цветы"],
        }
    },
    "Fruity": {
        "color": "#FF6B6B",
        "subcategories": {
            "Citrus": ["citrus", "цитрус", "lemon", "лимон", "orange", "апельсин",
                       "bergamot", "бергамот", "grapefruit", "грейпфрут", "lime", "лайм",
                       "tangerine", "мандарин", "yuzu", "юдзу"],
            "Stone Fruit": ["peach", "персик", "apricot", "абрикос", "plum", "слива",
                            "cherry", "вишня", "nectarine", "нектарин", "mango", "манго",
                            "lychee", "личи"],
            "Berry": ["berry", "ягода", "strawberry", "клубника", "raspberry", "малина",
                      "blackberry", "ежевика", "blueberry", "черника", "currant", "смородина",
                      "cranberry", "клюква", "gooseberry", "крыжовник", "raisin", "изюм"],
            "Tropical": ["tropical", "тропический", "pineapple", "ананас", "coconut", "кокос",
                         "passionfruit", "маракуйя", "papaya", "папайя", "guava", "гуава"],
            "Apple/Pear": ["apple", "яблоко", "pear", "груша", "quince", "айва"],
            "Dried Fruit": ["dried fruit", "сухофрукты", "fig", "инжир", "date", "финик",
                            "prune", "чернослив", "sultana"],
        }
    },
    "Vegetal": {
        "color": "#51CF66",
        "subcategories": {
            "Grassy": ["grass", "трава", "grassy", "травяной", "hay", "сено",
                       "fresh cut grass", "зеленый", "green", "spinach", "шпинат"],
            "Seaweed": ["seaweed", "морские водоросли", "marine", "ocean", "oceanic",
                        "nori", "нори", "sea", "морской"],
            "Vegetal (general)": ["vegetal", "vegetable", "овощной", "cucumber", "огурец",
                                  "peas", "горох", "asparagus", "спаржа", "zucchini"],
            "Herbaceous": ["herb", "трава", "mint", "мята", "thyme", "тимьян",
                           "basil", "базилик", "rosemary", "розмарин", "sage", "шалфей"],
        }
    },
    "Nutty & Toasty": {
        "color": "#FFA94D",
        "subcategories": {
            "Nutty": ["nut", "орех", "walnut", "грецкий орех", "almond", "миндаль",
                      "chestnut", "каштан", "hazelnut", "фундук", "peanut", "арахис",
                      "sesame", "кунжут", "pine nut", "кедровый орех"],
            "Roasted": ["roast", "roasted", "жареный", "toasted", "toast", "тост",
                        "baked", "выпечка", "malty", "солодовый", "malt", "солод"],
            "Caramel": ["caramel", "карамель", "caramelized", "toffee", "ириска",
                        "butterscotch", "burnt sugar"],
            "Cocoa": ["cocoa", "какао", "chocolate", "шоколад", "dark chocolate",
                      "горький шоколад", "mocha"],
        }
    },
    "Spicy": {
        "color": "#FF922B",
        "subcategories": {
            "Warm Spice": ["spice", "специи", "cinnamon", "корица", "clove", "гвоздика",
                           "cardamom", "кардамон", "star anise", "бадьян", "pepper", "перец",
                           "peppery", "перечный", "ginger", "имбирь", "nutmeg", "мускат"],
            "Pungent": ["pungent", "острый", "astringent", "вяжущий", "bitter", "горький",
                        "sharp", "резкий"],
        }
    },
    "Earthy": {
        "color": "#8B6914",
        "subcategories": {
            "Soil": ["earth", "земля", "earthy", "земляной", "soil", "loam",
                     "musty", "затхлый", "petrichor"],
            "Mushroom": ["mushroom", "гриб", "fungal", "трюфель", "truffle", "umami",
                         "умами", "forest floor", "лесная подстилка"],
            "Leather": ["leather", "кожа", "leathery", "кожаный", "tobacco", "табак",
                        "wood", "дерево", "woody", "деревянный", "cedar", "кедр",
                        "oak", "дуб", "pine", "сосна", "bark", "кора"],
            "Mineral": ["mineral", "минеральный", "stone", "камень", "slate", "сланец",
                        "chalk", "мел", "flint", "кремень", "wet stone"],
        }
    },
    "Sweet": {
        "color": "#FFD43B",
        "subcategories": {
            "Honey": ["honey", "мёд", "honeyed", "медовый", "nectar", "нектар"],
            "Vanilla": ["vanilla", "ваниль", "vanillin", "creamy", "сливочный",
                        "cream", "сливки", "milk", "молоко", "milky", "молочный"],
            "Syrup": ["syrup", "сироп", "molasses", "меласса", "treacle", "jaggery"],
            "Sweet (general)": ["sweet", "сладкий", "sweetness", "сладость", "sugary",
                                 "sugar", "сахар", "confection"],
        }
    },
    "Roasted & Smoky": {
        "color": "#495057",
        "subcategories": {
            "Smoke": ["smoke", "дым", "smoky", "дымный", "charcoal", "уголь",
                      "campfire", "костёр", "bonfire"],
            "Roasted Grain": ["grain", "зерно", "cereal", "злаки", "rice", "рис",
                              "barley", "ячмень", "oat", "овёс", "bread", "хлеб"],
            "Charred": ["char", "charred", "обугленный", "burnt", "горелый"],
        }
    },
    "Umami & Savory": {
        "color": "#74C0FC",
        "subcategories": {
            "Brothy": ["broth", "бульон", "savory", "пикантный", "soup", "суп",
                       "bouillon", "stock"],
            "Seaweed Umami": ["umami", "умами", "kelp", "ламинария", "dashi", "даши"],
            "Buttery": ["butter", "масло", "buttery", "маслянистый", "rich", "насыщенный"],
        }
    },
}

# All keywords flattened with their category/subcategory mapping
def build_keyword_map():
    mapping = {}
    for category, cat_data in FLAVOR_WHEEL.items():
        for subcategory, keywords in cat_data["subcategories"].items():
            for keyword in keywords:
                mapping[keyword.lower()] = {
                    "category": category,
                    "subcategory": subcategory,
                    "color": cat_data["color"],
                }
    return mapping

KEYWORD_MAP = build_keyword_map()

CATEGORY_COLORS = {cat: data["color"] for cat, data in FLAVOR_WHEEL.items()}
