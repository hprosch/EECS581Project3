def prune(potential_words, guess):
        clues = check(guess)

        # tuple list (letter, type (1,2,3), multiplicity)
        special_cases = []

        # prune based on all green letters
        for i in range(len(guess)):
            if clues[i] == 3:
                for j in range(len(potential_words)):
                    if potential_words[j][i] != guess[i]:
                        del potential_words[j]

        # prune based on all yellow guesses
        # same issue as grey
        for i in range(len(guess)):
            if clues[i] == 2:
                for j in range(len(potential_words)):
                    if guess[i] not in potential_words[j][i]:
                        del potential_words[j]

        # prune based on all grey letters
        # current implementation not quite right: dosen't account for guess with multiple of one letter with one grey
        for i in range(len(guess)):
            if clues[i] == 1:
                for j in range(len(potential_words)):
                    if guess[i] in potential_words[j][i]:
                        del potential_words[j]

        return potential_words

def prune(potential_words, guess):
        clues = check(guess)

        for i in range(len(potential_words)):

            delete = False
            
            # green case
            for j in range(len(guess)):
                if clues[j] == 3:
                    if potential_words[i][j] == guess[j]:
                        guess[j] = "_"
                    else:
                        delete = True

            # yellow case
            for j in range(len(guess)):
                if clues[j] == 2:
                    for k in range(len(guess)):
                        if potential_words[i][k] == guess[j]:
                            guess[j] == 

            # grey case
            for j in range(len(guess)):
                if clues[j] == 1:
                    ...
