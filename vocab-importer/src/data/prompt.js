const prompt = function(subject) {
  return `
Consider the following JSON Object:

{
	"words": [
		{
			"english": "boring",
			"kanji": "詰らない",
			"parts": "[{\"kanji\": \"\詰\", \"romaji\": [\"tsu\", \"ma\"]}, {\"kanji\": \"\ら\", \"romaji\": [\"ra\"]}, {\"kanji\": \"\な\", \"romaji\": [\"na\"]}, {\"kanji\": \"\い\", \"romaji\": [\"i\"]}]",
			"romaji": "tsumaranai"
		},
		{
			"english": "to speak",
			"kanji": "話す",
			"parts": "[{\"kanji\": \"\話\", \"romaji\": [\"ha\", \"na\"]}, {\"kanji\": \"\す\", \"romaji\": [\"su\"]}]",
			"romaji": "hanasu"
		},
		{
			"english": "to read",
			"kanji": "読む",
			"parts": "[{\"kanji\": \"\読\", \"romaji\": [\"yo\"]}, {\"kanji\": \"\む\", \"romaji\": [\"mu\"]}]",
			"romaji": "yomu",
		},
		{
			"english": "to shop",
			"kanji": "買い物する",
			"parts": "[{\"kanji\": \"\買\", \"romaji\": [\"ka\"]}, {\"kanji\": \"\い\", \"romaji\": [\"i\"]}, {\"kanji\": \"\物\", \"romaji\": [\"mo\", \"no\"]}, {\"kanji\": \"\す\", \"romaji\": [\"su\"]}, {\"kanji\": \"\る\", \"romaji\": [\"ru\"]}]",
			"romaji": "kaimonosuru",
		},
		{
			"english": "to lend",
			"kanji": "貸す",
			"parts": "[{\"kanji\": \"\貸\", \"romaji\": [\"ka\"]}, {\"kanji\": \"\す\", \"romaji\": [\"su\"]}]",
			"romaji": "kasu",
		}
	]
}

Write a json object with 12 words in the same way as the above examples.
The words must be related to the subject "${subject}"
`
}

export default prompt;