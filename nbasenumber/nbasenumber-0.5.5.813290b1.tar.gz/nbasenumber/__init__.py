#!/usr/bin/env python3
# coding-UTF-8

"""
nbasenumber

=====
How to pronounce
=====
"en bei s num ber".

=====
How to use
=====
Please see help(Base) after "from nbasenumber import Base".
"""

class Base(object) :
    """Create a mathematical integral number with n base.
  Base(num_base=10, digits=(), is_negative=False)
  num_base: requires an int > 1
  digits: requires a sequence that all indexes in it are >= 0 and < num_base,
          or an int. Ignore is_negative when digits is an int.
  e.g.
    Base(10, (1, 0, 4, 8, 5, 7, 6))
    Base(2, (1, 0, 0, 0, 1, 0, 1))
    Base(16, (12, 8, 9, 11, 15, 0, 1, 5), True)
  Create from an int:
    Base(10, tuple(int(i) for i in str(3750))) -> Base(10, (3, 7, 5, 0))
    Base(16) + Base(10, tuple(int(i) for i in str(252))) -> Base(16, (15, 12))
  Convert to another base:
    a = Base(10, (9, 6, 5, 0)) # 10-base(decimal)
    a = Base(16) + a # 16-base(hexadecimal)
    a = Base(2) + a # 2-base(binary)
    a = Base(8) + a # 8-base(octal)
    a = Base(3) + a # 3-base(ternary)
  Format and print:
    print(Base(12, (2, 8, 11, 10, 9)).format_to_str(_10="A", _11="B")) # 28BA9
"""
    
    def __init__(self, num_base=10, digits=(), is_negative=False) :
        """Initialize self.  See help(type(self)) for accurate signature."""
        
        try :
            num_base.__Base__
        except AttributeError :
            if type(num_base) != type(0) :
                raise TypeError("num_base must be an int, not "+\
                                str(type(num_base)))
            if num_base < 2 :
                raise ValueError("num_base must be greater than 1, got "+\
                                 str(num_base))
            self.__num_base = num_base
            if type(digits) == type(0) :
                self.__num_base = (Base(num_base)+digits).__num_base
                self.__digits = (Base(num_base)+digits).__digits
                self.__is_negative = (Base(num_base)+digits).__is_negative
            else :
                digits = tuple(digits)
                for i in digits :
                    if type(i) != type(0) :
                        raise TypeError("value in digits must be an int, not "+\
                                        str(type(i)))
                    if i < 0 :
                        raise ValueError("value in digits must be greater than \
-1, got "+str(i))
                    if i >= num_base :
                        raise ValueError("value in digits must be less than "+\
                                         str(num_base)+", got "+str(i))
                self.__digits = digits
                if is_negative and digits != () :
                    self.__is_negative = True
                else :
                    self.__is_negative = False
        else :
            self.__num_base = num_base.__Base__().__num_base
            self.__digits = num_base.__Base__().__digits
            self.__is_negative = num_base.__Base__().__is_negative
    @property
    def num_base(self) :
        return self.__num_base
    @property
    def digits(self) :
        return self.__digits
    @property
    def is_negative(self) :
        return self.__is_negative
    
    def __repr__(self) :
        """Return repr(self)."""
        
        return "-" * self.__is_negative + ("Base(%d, %s)"%(self.__num_base,
                                                           str(self.__digits)))
    
    def __Base__(self) :
        """Base(self)"""
        
        return Base(self.__num_base, self.__digits, self.__is_negative)
    
    def __int__(self) :
        """int(self)"""
        
        res = 0
        place = 0
        for i in self.digits[::-1] :
            res += i * self.num_base ** place
            place += 1
        if self.is_negative :
            return -res
        return res
    
    def __bool__(self) :
        """self != Base()"""
        
        return self.__digits != ()
    
    def __float__(self) :
        """floatt(self)"""
        
        return float(int(self))
    
    def __abs__(self) :
        """abs(self)"""
        
        return Base(self.__num_base, self.__digits)
    
    def __pos__(self) :
        """+self"""
        
        return Base(self.__num_base, self.__digits, self.__is_negative)
    
    def __neg__(self) :
        """-self"""
        
        return Base(self.__num_base, self.__digits, not(self.__is_negative))
    
    def __hash__(self) :
        """Return hash(self)."""
        
        return hash(int(self))
    
    def __eq__(self, value) :
        """Return self==value."""
        
        if type(value) == Base :
            return int(self) == int(value)
        elif type(value) == type(0) :
            return int(self) == value
        elif type(value) in (type(u""), type(b"")) :
            return False
        else :
            try :
                return int(self) == float(value)
            except Exception :
                return False
    
    def __ne__(self, value) :
        """Return self!=value."""
        
        if type(value) == Base :
            return int(self) != int(value)
        elif type(value) == type(0) :
            return int(self) != value
        elif type(value) in (type(u""), type(b"")) :
            return True
        else :
            try :
                return int(self) != float(value)
            except Exception :
                return True
    
    def __gt__(self, value) :
        """Return self>value."""
        
        if type(value) == Base :
            return int(self) > int(value)
        elif type(value) == type(0) :
            return int(self) > value
        elif type(value) in (type(u""), type(b"")) :
            return NotImplemented
        else :
            try :
                return int(self) > float(value)
            except Exception :
                return NotImplemented
    
    def __lt__(self, value) :
        """Return self<value."""
        
        if type(value) == Base :
            return int(self) < int(value)
        elif type(value) == type(0) :
            return int(self) < value
        elif type(value) in (type(u""), type(b"")) :
            return NotImplemented
        else :
            try :
                return int(self) < float(value)
            except Exception :
                return NotImplemented
    
    def __ge__(self, value) :
        """Return self>=value."""
        
        if type(value) == Base :
            return int(self) >= int(value)
        elif type(value) == type(0) :
            return int(self) >= value
        elif type(value) in (type(u""), type(b"")) :
            return NotImplemented
        else :
            try :
                return int(self) >= float(value)
            except Exception :
                return NotImplemented
    
    def __le__(self, value) :
        """Return self<=value."""
        
        if type(value) == Base :
            return int(self) <= int(value)
        elif type(value) == type(0) :
            return int(self) <= value
        elif type(value) in (type(u""), type(b"")) :
            return NotImplemented
        else :
            try :
                return int(self) <= float(value)
            except Exception :
                return NotImplemented
    
    def __add__(self, value) :
        """Return self+value."""
        
        if type(value) == Base :
            d_int = abs(int(self)+int(value))
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)+int(value)<0)
        else :
            if type(value) != type(0) :
                return NotImplemented
            d_int = abs(int(self)+value)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)+value<0)
    
    def __sub__(self, value) :
        """Return self-value."""
        
        return self + -value
    
    def __mul__(self, value) :
        """Return self*value."""
        
        if type(value) == Base :
            d_int = abs(int(self)*int(value))
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)*int(value)<0)
        else :
            if type(value) != type(0) :
                return NotImplemented
            d_int = abs(int(self)*value)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)*value<0)
    
    def __truediv__(self, value) :
        """Return self/value."""
        
        try :
            return float(self) / float(value)
        except Exception :
            return NotImplemented
    
    def __floordiv__(self, value) :
        """Return self//value."""
        
        if type(value) == Base :
            try :
                raw_input # check for Python 2 or Python 3
            except NameError :
                d_int = eval("abs(int(self)//int(value))")
            else :
                d_int = eval("abs(int(self)/int(value))")
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)*int(value)<0)
        else :
            if type(value) == type(0) :
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("abs(int(self)//value)")
                else :
                    d_int = eval("abs(int(self)/value)")
            else :
                try :
                    try :
                        raw_input # check for Python 2 or Python 3
                    except NameError :
                        d_int = eval("abs(int(int(self)//float(value)))")
                    else :
                        d_int = eval("abs(int(int(self)/float(value)))")
                except Exception :
                    return NotImplemented
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)*value<0)
    
    def __mod__(self, value) :
        """Return self%value."""
        
        if type(value) == Base :
            d_int = abs(int(self)%int(value))
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)%int(value)<0)
        else :
            if type(value) != type(0) :
                return NotImplemented
            d_int = abs(int(self)%value)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)%value<0)
    
    def __pow__(self, value, mod=None) :
        """Return pow(self, value, mod)."""
        
        if type(value) == Base :
            if mod == None :
                d_int = int(self) ** int(value)
            elif type(mod) == Base :
                d_int = int(self) ** int(value) % int(mod)
            elif type(mod) == type(0) :
                d_int = int(self) ** int(value) % mod
            else :
                return NotImplemented
            i_n = d_int < 0
            d_int = abs(d_int)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, i_n)
        else :
            if type(value) != type(0) :
                return NotImplemented
            if mod == None :
                d_int = int(self) ** value
            elif type(mod) == Base :
                d_int = int(self) ** value % int(mod)
            elif type(mod) == type(0) :
                d_int = int(self) ** value % mod
            else :
                return NotImplemented
            i_n = d_int < 0
            d_int = abs(d_int)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, i_n)
    
    def __divmod__(self, value) :
        """Return divmod(self, value)."""
        
        return (self.__floordiv__(value), self%value)
    
    def __lshift__(self, value) :
        """Return self<<value."""
        
        if type(value) == Base :
            d_int = abs(int(self)<<int(value))
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)<<int(value)<0)
        else :
            if type(value) != type(0) :
                return NotImplemented
            d_int = abs(int(self)<<value)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)<<value<0)
    
    def __rshift__(self, value) :
        """Return self>>value."""
        
        if type(value) == Base :
            d_int = abs(int(self)>>int(value))
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)>>int(value)<0)
        else :
            if type(value) != type(0) :
                return NotImplemented
            d_int = abs(int(self)>>value)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)>>value<0)
    
    def __and__(self, value) :
        """Return self&value."""
        
        if type(value) == Base :
            d_int = abs(int(self)&int(value))
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)&int(value)<0)
        else :
            if type(value) != type(0) :
                return NotImplemented
            d_int = abs(int(self)&value)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)&value<0)
    
    def __or__(self, value) :
        """Return self|value."""
        
        if type(value) == Base :
            d_int = abs(int(self)|int(value))
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)|int(value)<0)
        else :
            if type(value) != type(0) :
                return NotImplemented
            d_int = abs(int(self)|value)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)|value<0)
    
    def __xor__(self, value) :
        """Return self^value."""
        
        if type(value) == Base :
            d_int = abs(int(self)^int(value))
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)^int(value)<0)
        else :
            if type(value) != type(0) :
                return NotImplemented
            d_int = abs(int(self)^value)
            m_digits = ()
            while d_int != 0 :
                m_digits = (d_int%self.__num_base,) + m_digits
                try :
                    raw_input # check for Python 2 or Python 3
                except NameError :
                    d_int = eval("d_int // self.num_base")
                else :
                    d_int = eval("d_int / self.num_base")
            return Base(self.__num_base, m_digits, int(self)^value<0)
    
    def __not__(self) :
        return -self - 1
    
    def __invert__(self) :
        """~self"""
        
        return -self - 1
    
    def __round__(self, ndigits=None) :
        """Round self as a decimal."""
        
        if type(ndigits) == Base :
            ndigits = int(ndigits)
        elif ndigits == None or type(ndigits) == type(0) :
            pass
        else :
            return NotImplemented
        d_int = abs(round(int(self), ndigits))
        m_digits = ()
        while d_int != 0 :
            m_digits = (d_int%self.__num_base,) + m_digits
            try :
                raw_input # check for Python 2 or Python 3
            except NameError :
                d_int = eval("d_int // self.num_base")
            else :
                d_int = eval("d_int / self.num_base")
        return Base(self.__num_base, m_digits, round(int(self), ndigits)<0)
    
    def __radd__(self, value) :
        """Return value+self."""
        
        return value + int(self)
    
    def __rsub__(self, value) :
        """Return value-self."""
        
        return value - int(self)
    
    def __rmul__(self, value) :
        """Return value*self."""
        
        return value * int(self)
    
    def __rtruediv__(self, value) :
        """Return value/self."""
        
        return value / int(self)
    
    def __rfloordiv__(self, value) :
        """Return value//self."""
        
        try :
            raw_input
        except NameError :
            return eval("value // int(self)")
        else :
            return eval("value / int(self)")
    
    def __rmod__(self, value) :
        """Return value%self."""
        
        return value % int(self)
    
    def __rpow__(self, value, mod=None) :
        """Return pow(value, self, mod)."""
        
        return pow(value, int(self), mod)
    
    def __rand__(self, value) :
        """Return value&self."""
        
        return value & int(self)
    
    def __ror__(self, value) :
        """Return value|self."""
        
        return value | int(self)
    
    def __rxor__(self, value) :
        """Return value^self."""
        
        return value ^ int(self)
    
    def __rlshift__(self, value) :
        """Return value<<self."""
        
        return value << int(self)
    
    def __rrshift__(self, value) :
        """Return value>>self."""
        
        return value >> int(self)
    
    def format_to_str(self, **kwargs) :
        """self.format_to_str(**kwargs)
  self.format_to_str(_0="0", _1="1", _2="2", _3="3", _4="4", _5="5", _6="6",
                     _7="7", _8="8", _9="9", _10=..., _11=..., ...)"""
        for i in range(10) :
            try :
                kwargs["_"+str(i)]
            except KeyError :
                kwargs["_"+str(i)] = str(i)
        for i in range(self.__num_base) :
            try :
                kwargs["_"+str(i)]
            except KeyError :
                raise ValueError("value is missing for cipher "+str(i))
        if self.__digits == () :
            return kwargs["_0"]
        res = list(self.__digits)
        for i in range(self.__num_base) :
            for n in range(len(res)) :
                if res[n] == i :
                    res[n] = str(kwargs["_"+str(i)])
        return "-" * self.__is_negative + "".join(res)
    
    def arg(self) :
        """Thw arg() in complex."""
        
        from math import pi
        if self > Base() :
            return 2 * pi
        elif self < Base() :
            return pi
        else :
            raise ValueError("0 has no complex argument")
    
    def to_bytes(self, length, byteorder) :
        return int(self).to_bytes((length, int(length))[type(length)==Base],
                                  byteorder)
    
    def from_bytes(bytes, byteorder, num_base=256) :
        """Return a Base from this function. This is not used as a method."""
        
        return Base(num_base) + int.from_bytes(bytes, byteorder)
