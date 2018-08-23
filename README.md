# Fake News Detector For Circular Reporting
Helps detect fake news by analyzing the quality of the citations of a given website.

# Motivation
Recently, there has been increased public outrage over "fake news," or factually incorrect information that is deliberately circulated to mislead readers on the Internet. One way that malicious entities can spread false information is by creating a network of factually incorrect articles that cite one another as evidence, or by listing a series of citations that funnel back to one main source. This phenomenon is known as circular reporting. This project seeks to combat the spread of false information by developing an organized mechanism for checking sources.

# Description
Analyzes the references of a given website and reports how trustworthy it is. The detector works its way through 
generations of references and identifies each reference chain as an independent branch or a loop that connects to 
another branch. If it finds a reference that cites the original input website, a serious error is reported with the 
message: 'Circular citation was detected back to original url - untrustworthy!'

# To Run
In the command line, run 'python3 CircularCitationDetector.py [target_url] [MAX_GEN]'

# Input arguments
target_url: The url to be checked.

MAX_GEN: The maximum generation of references the detector will open and check. If MAX_GEN is 1, the detector will 
only open the input url and check its references. If MAX_GEN is 2, the detector will furthermore open the references 
of the input url and check the references to each of those references.

# Time To Run:
About 5^MAX_GEN seconds (experimentally determined)

# Definitions:
Loop: A reference that is touched by two independent chains of references forms a loop.

Branch: A chain of references that ends at a unique leaf (reference).

Miscellaneous refs: Online refs that do not start with the http or https protocol.

Circular citation: A descendant reference of the original url that cites the original url as one of its own references.

Generation: A direct reference of the target url belongs to generation 2. A direct reference of a gen-2 reference belongs
to generation 3, and so on and so forth.

Source: A unique website home. i.e. https://www.nytimes.com/apples-are-great and https://www.nytimes.com/cake-is-better 
are unique references, but have the same source, which is https://www.nytimes.com.

# Future Work:
While there are a series of validation tests implemented to ensure that each link found on a page is in fact a citation (rather than an ad, a link to the homepage, etc.), there are still some red herring links that are incorrectly identified by the detector as citations. For example, in the following links, the author byline and link to social media pages is positioned in close proximity to the content of the article, causing the detector to falsely identify it as a citation.
Examples:
https://www.nytimes.com/2012/10/14/magazine/buffalo-mozzarella-craig-ramini.html?pagewanted=all,
https://www.eater.com/2017/7/27/16021832/pizza-dipping-sauce-papa-johns-garlic-dominos-sauce

