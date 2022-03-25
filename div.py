import os, gzip
import re
import numpy as np
from  collections import Counter
from math import log
from scipy.optimize import curve_fit

def select(pattern, root='.'):
    """
    Select file matching a regular expression    

    Parameters
    ----------
    pattern : str
        A regular expresion.
    root : str, optional
        The path to the root folder. The default is '.'.

    Returns
    -------
    list of str
        list of paths to files in root 
        with filename matching the regular expression.

    """
    path = lambda folder, name: os.path.relpath(os.path.join(folder, name))
    paths = [path(folder, name) for folder, _, names in os.walk(root) for name in names]
    
    return list(filter(re.compile(pattern).fullmatch, sorted(paths)))                   

class Tokenizer():
    """
    Splits text into tokens
    A token is a sequence of contiguous alphanumeric characters with, 
    at least, one letter character 
    (for example, 1988 is not a valid token but B747 is). 
    Tokens may contain non-breaking characters such as dashes or apostrophes
    """
    char = '[^\W\d_]'
    alphanum = '[^\W_]'
    nonbreak = "[-'’`]"
    prefix = f'(?:{alphanum}+{nonbreak})'
    postfix = f'(?:{nonbreak}{alphanum}+)'
    pattern = f'{prefix}*{alphanum}*{char}{alphanum}*{postfix}*'
    rex = re.compile(pattern)    
        
    @staticmethod
    def split(text):
        """
        Tokenize text

        Parameters
        ----------
        text : str 
            input text.

        Returns
        -------
        list of str
            list of tokens in text.
        """
        return Tokenizer.rex.findall(text)
    

class Text():  
    """
    Read a text file and compute diversity
    """        
    @staticmethod
    def read_file(path):
        """
        Red the content of a text file
    
        Parameters
        ----------
        path : str
            the path to the input file.
    
        Raises
        ------
        NotImplementedError
            If the file format is not supported.
    
        Returns
        -------
        str
           The content in the text file.
    
        """
        if path.endswith('gz'):
            return gzip.open(path, 'rt', encoding='utf-8').read()
        elif path.endswith('zip') :
            raise NotImplementedError('zip format not yet implemented')              
        else:
            return open(path, 'r').read()
    
    def __init__(self, path, lowercase=True):
        """
        Read the specified file (text or gzipped text)

        Parameters
        ----------
        path : str
            The full filename.
        lowercase : boolean, optional
            Transform all tokens into lowercase if True. The default is True.
        """
        if os.path.exists(path):
            content = Text.read_file(path)
        else:
            content = path
        
        if lowercase:
            self._tokens_ = list(map(str.lower, Tokenizer.split(content)))
        else:
            self._tokens_ = Tokenizer.split(content)
    
        self._counter_ = Counter(self._tokens_)
        
    def __len__(self):
        """
        Returns
        -------
        int
            number of tokens in text.
        """
        return len(self._tokens_)
    
    def tokens(self):
        """
        Returns
        -------
        list of str
            list of tokens in text.
        """
        return self._tokens_
    
    def types(self):
        """
        Token types in text (unique tokens or dictionary entries)
        Returns
        -------
        list of str
            list of token types (unique tokens) in text.
        """
        return list(self._counter_.keys())
    
    
    @staticmethod
    def _diversity_(frequencies):
        """
        Parameters
        ----------
        frequencies : array of int/float
            Frequencies (absolute ro relative) of each group.

        Returns
        -------
        float
            Shannon diversity index for the element frequencies.

        """
        total = sum(frequencies)
        entropy = log(total, 2) - sum(f * log(f, 2) for f in frequencies) / total 

        return 2 ** entropy

    
    # return list of hapax legomena in text 
    # 
    def hapax_legomena(self):
        """
        hapax legomena are tokens with a single occurrence

        Returns
        -------
        list of str
            list of tokens with a single occurence in text.
        """
        return [k for k, v in self._counter_.items() if v == 1]
    
 
    def hapax_legomena_rate(self):
        """
        Returns
        -------
        float
            fraction of hapax legomena in text.

        """
        return len(self.hapax_legomena()) / self.__len__()
        
    def token_richness(self, step = 0):
        """
        Number of token types in text

        Parameters
        ----------
        step : int, optional
             if step > 0 return richness after n tokens
             with n a multiple of step (or the total number of tokens in text). 
             The default is 0.


        Returns
        -------
        int or dict of ints
            richness (number of token types in text) if step = 0
            richness evaluated at regular intervals of length = step.
        """
        if step == 0:
            return len(self.types())   
        else:
            stats = dict()
            token_types = set()
            for n, token in enumerate(self._tokens_, 1):
                token_types.add(token)
                if n % step == 0:
                    stats[n] = len(token_types)
            
            stats[n] = len(token_types)
            
            return stats
        
    def token_diversity(self, step = 0):
        """
        Compute the diversity of token types in text 
       
        Parameters
        ----------
        step : int, optional
             if step > 0 return all diversities after n tokens
             with n a multiple of step (or the total number of tokens in text). 
             The default is 0.

        Returns
        -------
        float or dict of floats
            Shannon diversity index for this text if step = 0 
            Shannon diversity index evaluated at regular intervals
            of length = step.
        """
        if step == 0:
            return Text._diversity_(self._counter_.values())
        else:
            c = Counter()
            stats = dict()
            for n, token in enumerate(self._tokens_, 1):
                c[token] += 1
                if n % step == 0:
                    stats[n] = Text._diversity_(c.values())
            
            stats[n] = Text._diversity_(c.values())
            
            return stats
    
   
    def dict_size(self, step = 0):
        """
        Compute the dictionary size (number of token types) in the text.

        Parameters
        ----------
        step : int, optional
            if step > 0 return dict with number of types after n tokens
            with n a multiple of step or the total number of tokens in text.
            The default is 0.

        Returns
        -------
        int
             number of token types in text if step = 0,
             number of token types after regular intervals  
             of length = step, otherwise
        """
        if step == 0:
            return len(self._counter_)
        else:
            c = Counter()
            stats = dict()
            for n, token in enumerate(self._tokens_, 1):
                c[token.lower()] += 1
                if n % step == 0:
                    stats[n] = len(c)
                    
            stats[n] = len(c)
            
            return stats
    

class BestFit(object):
    """
    Fit data points to the specified function    
    """
    
    def exp3(x, y0, yM, xmid):
        """
        Saturating exponential with 3 parameters
        Parameters
        ----------
        y0 : intercept.
        yM : asymptotic value.
        xmid : x-value for y = (y0 + yM) / 2.
        """
        return y0 + (yM - y0) * ( 1 - np.exp(x * log(0.5) / xmid))

    
    def exp2(x, yM, xmid):
        """
        Saturating exponential with 2 parameters 
        
        Parameters
        ----------
        yM : asymptotic value.
        xmid : x-value for y = (y0 + yM) / 2.
        """
        return yM * (1 - np.exp(x * log(0.5) / xmid))

   
    def logistic(x, yM, slope):
        """
        Logistic function

        Parameters
        ----------
        yM : asymptotic value.
        slope: slope at midpoint.
        """
        return yM * (1 / (1 + np.exp(-x / slope)) - 0.5)
    
    
    def bio_model2(x, yM, b):
        """
        Model 2 in Colwell et all 1994
        """
        return yM * x / (x + b)
    
    def bio_model3(x, yM, b, c):
        """ 
        A generalization of the model above.
        """
        return yM * (x + b) / (x + c)
    
  
    def power(x, yM, alpha, c):
       """
       General power function 
       Parameters
       ----------
       yM: asympotic value
       alpha: exponent
       """
       return yM * (x  / (x + c)) ** alpha
       
    def simple_power(x, C, alpha):
        """
        A simple power function with exponent alpha
        """
        return C * x ** alpha
    
   
    def zipf(x, C, alpha):
        """
        Zipfean distribution with constant C and exponent alpha
        """
        return C / x ** alpha  
    
   
    def linear(x, a, b):
        """
         A simple linear model
        """
        return a * x + b
    
    def __init__(self, name='exp1'):
        """
        Create object to identify optimal parameters for the sepecified function.

        Parameters
        ----------
        name : str, optional
            The type of function. The default is 'exp1'.

        Raises
        ------
        NotImplementedError
            If the function name has not been implemented.

        """
        try:
            self.func = getattr(BestFit, name)
            self.params = None
        except AttributeError:
            raise NotImplementedError(name)
        
  
    def fit(self, X, Y, **args):
        """
        Compute the best fit parameters      

        Parameters
        ----------
        X : array of float
            x-values.
        Y : array of float
            y-values.
        **args : params
            optional parameters to be passed to scipy.optimize.curve_fit.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        self.params = curve_fit(self.func, X, Y, **args)[0]
        
        return self.params
    
   
    def f(self, X, *params):
        """
        Parameters
        ----------
        X : array of float
            x-values.
        *params : floats
            parameters for the invoked function, such as slope and intercept.

        Returns
        -------
        array of float
           array of Y-values for an input array X.

        """
        if len(params) > 0:
            return self.func(X, *params)
        else:
            return self.f(X, *self.params)

def richness(items):
    """
    Parameters
    ----------
    items : iterable 
        a collection of repeatable elements.

    Returns
    -------
    int
        the number of unique items in the collectin.

    """
    return len(set(items))
           
def shannon_diversty_index(items):
    """
    Parameters
    ----------
    items : iterable
        a collection of repeatable elements.

    Returns
    -------
    float
        Shannon diversity index for the iterable collection.

    """
    frequencies = Counter(items).values()
    total = sum(frequencies)
    entropy = log(total, 2) - sum(f * log(f, 2) for f in frequencies) / total 

    return 2 ** entropy

def dr_rate(items):
    """
    Parameters
    ----------
    items : iterable
         a collection of repeatable elements.

    Returns
    -------
    float
        ratio between Shannon diversity and richness of the collection.

    """
    return shannon_diversty_index(items) / richness(items)


        