from json import JSONEncoder

def alpha(obj):
  return json.dumps(obj)

class A(JSONEncoder):
  a = 1;
  b = 2;

  def __init__(self, a, b):
        self.a = a
        self.b = b

  @property
  def serialize(self):
      return {
          "a": self.a,
          "b": self.b
      }


a = A(3, 4)
print(alpha(a))