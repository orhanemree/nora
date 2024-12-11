# HTML
HTML parser library from scratch.

## Features
* Implemented all tokens for the tokenizer.
* Implemented all states in the tokenizer except character references.
* Implemented essential nodes for the parser. (Document, DocumentType, Comment, Element, Text)
* Implemented essential insertion modes in the parser. (Initial, BeforeHTML, BeforeHead, InHead, AfterHead, InBody, Text, AfterBody, AfterAfterBody)

## What I've Learned
* I have read a whole standard to parse HTML source and many times some parts again and again. It was 40% programming and 60% reading specification which is sometimes hard and boring.

## References
* [HTML Standard](https://html.spec.whatwg.org/multipage/)
* [Let's Tokenize HTML by Andreas Kling [Video]](https://youtu.be/7ZdKlyXV2vw?si=J-hktFU9SypmTAT3)
* [Let's Parse HTML by Andreas Kling [Video]](https://youtu.be/16DEBJ1TI3Q?si=cVwmrjU49tSO8DEg)