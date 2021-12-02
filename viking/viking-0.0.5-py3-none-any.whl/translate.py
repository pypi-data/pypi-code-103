import os, sys
try:
    from tqdm import tqdm
    from reflect import Database, Value, Identity
except ImportError:
    sys.exit("Install Requirements")

def main():

    print("{}File: {}".format("\u001b[34m", "\u001b[0m"), end="")

    file_path = input()

    print("{}Line per second: {}".format("\u001b[34m", "\u001b[0m"), end="")
    ratio = int(input())

    if os.path.exists(file_path):
        with open(file_path) as f:
            data = f.read()
        
        past = []
        past_badge = 0
        past_split = [0, 0]
        bakery = ""
        for i, data in tqdm(enumerate(data.splitlines()), desc="Converting File"):
            coords = data.split(",")
            x = int(float(coords[0])-float(past_split[0]))
            y = int(float(coords[1])-float(past_split[1]))
            zero = float("0.0")
            
            # Create Dynamic Badge ABS (Convert - and + to +)
            x_dyn = abs(x)
            y_dyn = abs(y)
                
            if x == zero:
                x = "~"
            if y == zero:
                y = "~"

            if data != past:
                badge = past_badge+(x_dyn*ratio)+(y_dyn+ratio)
                bakery += f"{badge} goto {x} {y}\n"
                past_badge = badge # Now that it isnt refrenced, you can create a future refrence
            past = data
            past_split = data.split(",")
        
        print("{}Extracted Instruction file: ".format("\u001b[34m"), end="")

        with open(input(), "w") as f:
            f.write(bakery)

        print("{}Extracted Reflect Database File (Leave empty do disable): ".format("\u001b[34m"), end="")
        # This is for eventually having software load reflect to Instruction, as reflect has a trend system that could work with swerve
        # This script uses Reflect backend syntax to maximize speed, not checking for input errors

        inp = input()

        if not inp == "":
            print("{}{}{}Creating Reflect File".format("\u001b[36m", "\u001b[34m", "\u001b[1m\u001b[31m"))

            db = Database(inp)
            if os.path.exists(inp):
                sys.exit("ReflectDB File already exists!")
            else:
                db.create_all()

            with open(file_path) as f:
                data = f.read()

            basket = []
            for i, data in tqdm(enumerate(data.splitlines())):
                coords = data.split(",")
                egg = {
                    "x": coords[0],
                    "y": coords[1],
                    "id": "AUTOFILL"
                }
                basket.append(db.dumps(egg))

            for i in basket:
                db.publish(i)

            print("{}Finished File: ".format("\u001b[34m"), end="")

if __name__ == "__main__":
    main()