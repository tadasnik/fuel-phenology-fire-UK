import tomli

torange = (1.0, 0.4980392156862745, 0.054901960784313725)
tblue = (0.12156862745098039, 0.4666666666666667, 0.7058823529411765)
tgreen = (0.17254901960784313, 0.6274509803921569, 0.17254901960784313)
tpurple = (0.5803921568627451, 0.403921568627451, 0.7411764705882353)
tpink = (0.8901960784313725, 0.4666666666666667, 0.7607843137254902)
tbrown = (0.5490196078431373, 0.33725490196078434, 0.29411764705882354)
tchaki = (0.7372549019607844, 0.7411764705882353, 0.13333333333333333)
tred = (0.8392156862745098, 0.15294117647058825, 0.1568627450980392)

ukceh_classes = {
    1: "Deciduous woodland",
    2: "Coniferous woodland",
    3: "Arable",
    4: "Improved grassland",
    5: "Neutral grassland",
    6: "Calcareous grassland",
    7: "Acid grassland",
    8: "Fen",
    9: "Heather",
    10: "Heather grassland",
    11: "Bog",
    12: "Inland rock",
    13: "Saltwater",
    14: "Freshwater",
    15: "Supralittoral rock",
    16: "Supralittoral sediment",
    17: "Littoral rock",
    18: "Littoral sediment",
    19: "Saltmarsh",
    20: "Urban",
    21: "Suburban",
}

ukceh_classes_n = {
    1: "Deciduous\nwoodland",
    2: "Coniferous\nwoodland",
    3: "Arable",
    4: "Improved\ngrassland",
    5: "Neutral\ngrassland",
    6: "Calcareous\ngrassland",
    7: "Acid\ngrassland",
    8: "Fen",
    9: "Heather",
    10: "Heather\ngrassland",
    11: "Bog",
    12: "Inland\nrock",
    13: "Saltwater",
    14: "Freshwater",
    15: "Supralittoral\nrock",
    16: "Supralittoral\nsediment",
    17: "Littoral\nrock",
    18: "Littoral\nsediment",
    19: "Saltmarsh",
    20: "Urban",
    21: "Suburban",
}

color_dict = {
    0: "white",
    1: tgreen,
    2: tblue,
    3: tchaki,
    4: tchaki,
    7: torange,
    9: tpink,
    10: tbrown,
    11: tpurple,
    21: tred,
}


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)
