from radon.radon.visitors import ComplexityVisitor, HalsteadVisitor
from radon.radon.metrics import HalsteadReport
from Search import Search,part_Holder

v = ComplexityVisitor(True,Search)
print(v.functions)