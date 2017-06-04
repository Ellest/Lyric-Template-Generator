import markovify

with open("data/ed_sheeran_give_me_love.txt") as f:
	text = f.read()

text_model = markovify.Text(text)

for i in range(50):
    print(text_model.make_short_sentence(140))