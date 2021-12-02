# ---------------------------------------------------------------------------------------------------------------------
# Alexis MC - V0.1 - 15/11/2021 Creation of the python DEMIX library
# Alexis MC - V0.2 - 17/11/2021 Added several useful lists to be used
# ---------------------------------------------------------------------------------------------------------------------

dem_list = ["SRTMGL1", "CopDEM_GLO-30", "ASTERGDEM", "ALOS_World_3D", "Copernicus_DEM", "NASADEM"]

supported_dem_list = ["CopDEM_GLO-30", "SRTMGL1", "ASTERGDEM" ,"ALOS_World_3D"]

criterion_list = [("A01", "Product fractional cover"),
                  ("A02", "Valid data fraction"),
                  ("A03", "Primary data"),
                  ("A04", "Valid land fraction"),
                  ("A05", "Primary land fraction")]

layer_list = ["Heights", "validMask", "SourceMask", "landWaterMask" ]

demix_tile_example = ["N35YE014F", "N64ZW019C"]
