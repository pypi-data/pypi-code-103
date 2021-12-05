#!/usr/bin/python3
from totptray import totptray
import unittest
import pyperclip

class Test(unittest.TestCase):
    standardMenuItems = 3
    def test_icon_creation(self):
        icon = totptray._create_icon()
        try:
            icon.verify()
        except:
            self.fail("Icon does not pass verification!")

        self.assertTrue(icon.width > 1)
        self.assertTrue(icon.height > 1)
    
    def test_copy_code(self):
        #Clear the clipboard.
        pyperclip.copy("")
        try:
            totptray._copy_code("test")
        except:
            self.fail("Got an exception while calling _copy_code!")

        code = pyperclip.paste()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_create_menu_empty(self):
        menu = totptray._create_menu("")
        self.assertEqual(len(menu), 0+ self.standardMenuItems)

    def test_create_menu_one(self):
        menu = totptray._create_menu((("label","key"),))
        self.assertEqual(len(menu), 1 + self.standardMenuItems)
        self.assertEqual(menu[0].text, "label")

    def test_create_menu_multiple(self):
        menu = totptray._create_menu((("label0","key0"),("label1","key1"),("label2","key2")))
        self.assertEqual(len(menu), 3+ self.standardMenuItems)
        for idx, item in enumerate(menu):
            if idx == len(menu) - self.standardMenuItems:
                break
            self.assertEqual(item.text, "label" + str(idx))

    def test_create_menu_multiple_different_codes(self):
        menu = totptray._create_menu((("label0","AAAAAAAAAAAAAAAA"),("label1","BBBBBBBBBBBBBBBB"),("label2","CCCCCCCCCCCCCCCC")))
        self.assertEqual(len(menu), 3 + self.standardMenuItems)
        codes=set()

        for idx, item in enumerate(menu):
            if idx == len(menu) - self.standardMenuItems:
                break
            self.assertEqual(item.text, "label" + str(idx))
            item._action(None)
            codes.add(pyperclip.paste())
        self.assertEqual(len(codes), 3)

    def test_create_menu_incorrect(self):
        self.assertRaises(AssertionError, totptray._create_menu, (("label=key",),))

if __name__ == '__main__':
    unittest.main()
