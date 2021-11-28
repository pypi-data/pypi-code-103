import math
import matplotlib.pyplot as plt
from .Generaldistribution import Distribution

class Binomial(Distribution):
    
    """ Binomial distribution class for calculating and 
    visualizing a Binomial distribution.
    
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data_list (list of floats) a list of floats to be extracted from the data file
        p (float) representing the probability of an event occurring
        n (int) the total number of trials
  
            
    """
    
        # A binomial distribution is defined by two variables: 
        #   p, which is the probability of getting a positive outcome
        #   n, which is the number of trials

        # If you know these two values, you can calculate the mean and the standard deviation
        #       
        # For example, if you flip a fair coin 25 times, p = 0.5 and n = 25
        # You can then calculate the mean and standard deviation with the following formula:
        #   mean = p * n
        #   standard deviation = sqrt(n * p * (1 - p))

        #       
    
    def __init__(self, prob=.5, size=20):
        
        # 
        # init function from the Distribution class to initialize the
        # mean and the standard deviation of the distribution
        #   p: probability of the distribution
        #   n: size of the distribution 
        #
        
        self.n = size
        self.p = prob
        
        mean = self.calculate_mean()
        stdev = self.calculate_stdev()
        
        Distribution.__init__(self, mean, stdev)
                      
    
    def calculate_mean(self):
    
        """Function to calculate the mean of the Binomial distribution from p and n
        
        Args: 
            None
        
        Returns: 
            float: mean of the data set
    
        """
        
        self.mean = self.p * self.n
                
        return self.mean 


    def calculate_stdev(self):

        """Function to calculate the standard deviation from p and n.
        
        Args: 
            None
        
        Returns: 
            float: standard deviation of the data set
    
        """
        
        self.stdev = math.sqrt(self.n * self.p * (1 - self.p))
        
        return self.stdev
        
        
        
    def replace_stats_with_data(self):
    
        """Function to calculate p and n from the data set
        
        Args: 
            None
        
        Returns: 
            float: the p value
            float: the n value
    
        """        
        
        #
        # replace_stats_with_data(): 
        #   - updates the n attribute of the binomial distribution
        #   - updates the p value of the binomial distribution by calculating the
        #       number of positive trials divided by the total trials
        #   - updates the mean attribute
        #   - updates the standard deviation attribute
        #           
   
        self.n = len(self.data)
        self.p = 1.0 * sum(self.data) / len(self.data)
         
        self.mean = self.calculate_mean()
        self.stdev = self.calculate_stdev()   
        
        return self.p, self.n
        

        
    def plot_bar(self):
        
        """Function to output a bar chart of the instance variable data using 
        matplotlib pyplot library.
        
        Args:
            None
            
        Returns:
            None
        """
            
        # plot_bar():
        #   - creates a bar chart of the data
        #       The x-axis has a value of zero or one
        #       The y-axis has the count of results for each case
        #
        #   For example, say you have a coin where heads = 1 and tails = 0.
        #   If you flipped a coin 35 times, and the coin landed on
        #   heads 20 times and tails 15 times, the bar chart would have two bars:
        #   0 on the x-axis and 15 on the y-axis
        #   1 on the x-axis and 20 on the y-axis

        
        plt.bar(x= ['0','1'], height = [(1 - self.p) * self.n, self.p * self.n])
        plt.title ('Bar Chart of Data')
        plt.xlabel('outcome')
        plt.ylabel('count')
      
        
    def pdf(self, k):
        
        """Probability density function calculator for the binomial distribution.
        
        Args:
            k (float): point for calculating the probability density function
            
        
        Returns:
            float: probability density function output
        """
        
        # pdf(k):
        #   calculates the probability density function for a binomial distribution
        #   For a binomial distribution with n trials and probability p, 
        #   the probability density function calculates the likelihood of getting
        #   k positive outcomes. 
        # 
        #   For example, if you flip a coin n = 60 times, with p = .5,
        #   what's the likelihood that the coin lands on heads 40 out of 60 times?
        #   f(k,n,p)= binomial_coeff(n,k) * (p ** k) * (1 - p) ** (n - k)
        
        binomial_coeff_n_k = math.factorial(self.n)/(math.factorial(k) * math.factorial (self.n-k))
        
        return binomial_coeff_n_k * (self.p ** k) * (1 - self.p) ** (self.n - k)


    def plot_bar_pdf(self):

        """Function that creates the bar chart that plots the pdf of the binomial distribution
        
        Args:
            None
        
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
            
        """
    
        # plot_bar_pdf(): 
        #   bar chart that plots the probability density function from
        #   k = 0 to k = n
        #   This method also returns the x and y values used to make the chart
        
        x = []
        y = []        
        
          
        # calculate the x values to visualize
        for k in range (self.n+1):
        
            x.append(k)
            y.append(self.pdf(k))
            
        # make the plots   
        plt.bar(x, y)
        plt.title('Distribution of Outcomes')
        plt.ylabel('Probability')
        plt.xlabel('Outcome')

        plt.show()

        return x, y        
        
        
                
    def __add__(self, other):
        
        """Function to add together two Binomial distributions with equal p
        
        Args:
            other (Binomial): Binomial instance
            
        Returns:
            Binomial: Binomial distribution
            
        """
        
        try:
            assert self.p == other.p, 'p values are not equal'
        except AssertionError as error:
            raise
        
        # __add__(other): 
        #   addition for two binomial distributions. It is assumed that the
        #   p values of the two distributions are the same.
        #   the try, except statement above will raise an exception if the p values are not equal.
        #   When adding two binomial distributions, the p value remains the same
        #   The new n value is the sum of the n values of the two distributions.  
            
        result = Binomial()
        
        result.n = self.n + other.n
        result.p = self.p
        
        result.mean = result.calculate_mean
        result.stdev = result.calculate_stdev
        
        return result
        
        
    def __repr__(self):
    
        """Function to output the characteristics of the Binomial instance
        
        Args:
            None
        
        Returns:
            string: characteristics of the Gaussian
        
        """
        
        # __repr__(): 
        #   representation method so that the output looks like
        #       mean 5, standard deviation 4.5, p .8, n 20

        return "mean {}, standard deviation {}, p {}, n {}".format(self.mean, self.stdev, self.p, self.n)
