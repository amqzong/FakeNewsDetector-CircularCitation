# FakeNewsDetector-CircularCitation
Helps detect fake news by analyzing the quality of references of a given website.

# Description
Analyzes the references of a given website and reports how trustworthy it is. The detector works its way through 
generations of references and identifies each reference chain as an independent branch or a loop that connects to 
another branch. If it finds a reference that cites the original input website, a serious error is reported with the 
message: 'Circular citation was detected back to original url - untrustworthy!'

# To Run
# In the command line, run 'python3 CircularCitationDetector.py [target_url] [MAX_GEN]'

# Input arguments
target_url: The url to be checked.

MAX_GEN: The maximum generation of references the detector will open and check. If MAX_GEN is 1, the detector will 
only open the input url and check its references. If MAX_GEN is 2, the detector will furthermore open the references 
of the input url and check the references to each of those references.

# Definitions:
Loop: A reference that is touched by two independent chains of references forms a loop.

Branch: A chain of references that ends at a unique leaf (reference).

Miscellaneous refs: Online refs that do not start with the http or https protocol.

Circular citation: A descendant reference of the original url that cites the original url as one of its own references.

Generation: A direct reference of the target url belongs to generation 2. A direct reference of a gen-2 reference belongs
to generation 3, and so on and so forth.

Source: A unique website home. i.e. https://www.nytimes.com/apples-are-great and https://www.nytimes.com/cake-is-better 
are unique references, but have the same source, https://www.nytimes.com.

# To do
Problems with footer: 
https://www.nytimes.com/2012/10/14/magazine/buffalo-mozzarella-craig-ramini.html?pagewanted=all,
https://www.eater.com/2017/7/27/16021832/pizza-dipping-sauce-papa-johns-garlic-dominos-sauce

# Timing:
About 5^MAX_GEN seconds
