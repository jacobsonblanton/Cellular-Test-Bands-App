import math

psq = [i for i in range(100, 0, -1) if math.sqrt(i).is_integer() is True]
print(psq)
