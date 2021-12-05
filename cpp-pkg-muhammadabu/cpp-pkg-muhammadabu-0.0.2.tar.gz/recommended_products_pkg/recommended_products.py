import random

class RecommendedProduct:
    
    def generate_random(self, number):
        
        randomlist=[]
        for x in range (3):
            n=random.randint(0,len(number)-1)
            print(n)
            randomlist.append(number[n])
            number.pop(n)
        return randomlist
        
if __name__ == '__main__':
    rp=RecommendedProduct()
    number=10
    
    inputNum=[1,2,3,4,5]
    
    print(len(inputNum))
    randomlist=[]
    #for x in range (3):
        
    rand=rp.generate_random(inputNum)
    #randomlist.append(rand)
    print('\n Random number:{}'.format(rand))
      
    #print(randomlist) 