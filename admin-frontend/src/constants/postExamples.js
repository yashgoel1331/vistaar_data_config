export const POST_EXAMPLES = {
  glossary: `{
  "snapshot": {
    "milk": {
      "gu": ["દૂધ"],
      "transliteration": ["dudh"]
    }
  }
}`,

  forbidden: `{
  "snapshot": {
    "milk injection": "This practice is harmful and not recommended.",
    "increase milk artificially": "Do not suggest harmful or illegal methods."
  },
  "note": "updated forbidden rules"
}`,

  preferred: `{
  "snapshot": {
    "milk injection": "This practice is harmful and not recommended.",
    "increase milk artificially": "Do not suggest harmful or illegal methods."
  },
  "note": "updated preferred rules"
}`,

  schemes: `{
  "snapshot": {
    "aif": "Agriculture Infrastructure Fund (AIF)",
    "bksy": "Dr. Babasaheb Ambedkar Krushi Swavalamban Yojna",
    "agroforestry": "Nanaji Deshmukh Krishi Sanjivani Prakalp Agroforestry"
  },
  "note": "updated schemes list"
}`,

  aliasesEnGu: `{
  "snapshot": {
    "udder": ["આંચળ", "આળ"]
  }
}`,

  aliasesEnglish: `{
  "snapshot": {
    "udder": ["teat", "mammary"]
  }
}`,

  ambiguousTerms: `{
  "snapshot": [
    {
      "gu_terms": ["બેંક"],
      "type": "ask",
      "rule": "Could refer to river bank or financial bank"
    }
  ]
}`,
};
