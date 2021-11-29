from ottopy import get_robo_builder
import random


def turn_right(world):
    world.add_home_goal(random.randint(1, 10), 1)


def params(world):
    choices = ['apple', 'banana', 'strawberry', 'carrot', 'tulip']
    obj = random.choice(choices)
    world.add_object(2, 1, obj, 1)
    random.shuffle(choices)
    world.add_home_goal(7, 2)
    for x in range(len(choices)):
        world.add_object(x+2, 2, choices[x], 1)
        if choices[x] == obj:
            world.add_pick_obj_goal(x+2, 2, choices[x], 1)


def params_2(world):
    choices = ['apple', 'banana', 'strawberry',
               'carrot', 'tulip', 'star', 'leaf']
    obj = random.sample(choices, 3)
    world.add_object(2, 1, obj[0], 1)
    world.add_object(3, 1, obj[1], 1)
    world.add_object(4, 1, obj[2], 1)

    random.shuffle(choices)
    world.add_home_goal(9, 2)
    for x in range(len(choices)):
        world.add_object(x+2, 2, choices[x], 1)
        if choices[x] in obj:
            world.add_pick_obj_goal(x+2, 2, choices[x], 1)


def params_multiple(world):
    choices = ['apple', 'banana', 'strawberry']
    exce = ['carrot', 'tulip', 'star', 'leaf']
    for x in range(3):
        for y in range(random.randint(5, 8)):
            val = random.randint(0, 2)
            if val > 0:
                world.add_object(y+2, x+2, choices[x], 1)
                world.add_pick_obj_goal(y+2, x+2, choices[x], 1)
            else:
                world.add_object(y+2, x+2, random.choice(exce), 1)


def middle(world):
    cols = random.choice([5, 7, 9, 11])
    world.set_dimensions(1, cols)
    world.add_object(cols//2 + 1, 1, 'star', 1)
    world.add_pick_obj_goal(cols//2 + 1, 1, 'star', 1)


def pick_all(world):
    choices = ['apple', 'banana', 'strawberry', 'carrot', 'tulip']
    choice = random.choice(choices)


def choose_fruit():
    choice = random.randint(1, 3)
    if choice == 1:
        return 'apple'
    elif choice == 2:
        return 'banana'
    else:
        return 'strawberry'


def pick_fruits(world):
    cfruit = 0
    # Fruit to pick
    fruit = choose_fruit()
    world.add_object(3, 1, fruit, 1)
    for x in range(3, 9):
        for y in range(3, 9):
            f = choose_fruit()
            counter = random.randint(1, 5)
            world.add_object(x, y, f, counter)
            if f == fruit:
                cfruit += counter

    world.add_repoter_goal("I counted {} {}".format(cfruit, fruit))


def swap(world):
    cols = world.cols
    for x in range(cols - 2):
        world.add_object(x + 2, 1, 'apple', 1)
        world.add_object(x + 2, 2, 'banana', 1)
    world.add_home_goal(1, 2)


def lower_triangle(world):
    dim = random.choice([7, 9, 11, 13, 15])
    world.set_dimensions(dim//2+2, dim)
    size = dim//2 + 1
    dimond_size = dim - 2
    stars = 0
    for y in range(0, size - 1):
        for x in range(0, y + 1):
            world.add_drop_obj_goal(size+x, y+2,  'star', 1)
            stars += 1

    for y in range(1, size - 1):
        for x in range(1, y + 1):
            world.add_drop_obj_goal(size-x, y+2,  'star', 1)
            stars += 1
    world.add_object(1, 1, 'star', stars)


def swap_bot(bot):
    bot.max_capacity = 1


def jump(world):
    choice = random.randint(1, 9)
    for x in range(10):
        if choice != x+1:
            world.add_wall(x+1, 10, "south")
        else:
            for y in range(9, 5, -1):
                world.add_wall(x+1, y, "east")
                world.add_wall(x+1, y, "west")
            world.add_wall(x+1, 5, "north")
            world.add_flag(x+1, 6)
    world.add_flag_count_goal(1)


def jump_multi(world):
    choice = random.sample(range(2, 9, 2), 3)
    for x in range(10):
        if x not in choice:
            world.add_wall(x+1, 10, "south")
        else:
            t = random.randint(2, 7)
            for y in range(9, t, -1):
                world.add_wall(x+1, y, "east")
                world.add_wall(x+1, y, "west")
            world.add_wall(x+1, t, "north")
            world.add_flag(x+1, t+1)
    world.add_flag_count_goal(3)
    world.add_home_goal(10, 10)


get_robo = get_robo_builder(levels={
    'turn_right': turn_right,
    'params': params,
    'params-2': params_2,
    'test': params_multiple,
    'middle': middle,
    'pick_all': pick_all,
    'pick_fruits': pick_fruits,
    'lower_triangle': lower_triangle,
    'swap': swap,
    'jump': jump,
    'jump_multi': jump_multi
}, robo_fn={
    'swap': swap_bot
})
