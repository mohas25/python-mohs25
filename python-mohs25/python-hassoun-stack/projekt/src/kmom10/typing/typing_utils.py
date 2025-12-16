# Hjälpfunktioner och beräkningslogik
# Krav: inga klasser, inga list/dict comprehensions, ingen zip, inga lambda

import os
import time

# Filnamnskonstanter (ska vara engelska och versaler)
EASY_FILE = "easy.txt"
MEDIUM_FILE = "medium.txt"
HARD_FILE = "hard.txt"
SCORES_FILE = "scores.txt"

ANIMAL_THRESHOLDS = (
    (0, 5, "Sloth", "Sengångare"),
    (6, 15, "Snail", "Snigel"),
    (16, 30, "Manatee", "Manat"),
    (31, 40, "Human", "Människa"),
    (41, 50, "Gazelle", "Gasell"),
    (51, 60, "Ostrich", "Struts"),
    (61, 70, "Cheetah", "Gepard"),
    (71, 80, "Swordfish", "Svärdfisk"),
    (81, 90, "Spur-winged goose", "Sporrgås"),
    (91, 100, "White-throated needletail", "Taggsvale"),
    (101, 120, "Golden eagle", "Kungsörn"),
    (121, 10000, "Peregrine falcon", "Pilgrimsfalk"),
)

def read_lines(path):
    """Read all lines from file, strip trailing newlines; keep empty lines as ""."""
    lines = []
    f = None
    try:
        f = open(path, "r", encoding="utf-8")
        for raw in f:
            line = raw.rstrip("\n").rstrip("\r")
            lines.append(line)
    finally:
        if f is not None:
            f.close()
    return lines

def split_words(line):
    """Split on spaces, preserve punctuation as part of words. Multiple spaces are separators."""
    parts = []
    current = ""
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == " ":
            if current != "":
                parts.append(current)
                current = ""
        else:
            current = current + ch
        i += 1
    if current != "":
        parts.append(current)
    return parts

def update_histogram_word(hist, word):
    """Increment count for word in dict hist."""
    if word in hist:
        hist[word] = hist[word] + 1
    else:
        hist[word] = 1

def compute_line_stats(target_line, user_line, cumulative_hist):
    """Compare target vs user for one line.

    Returns tuple:
      (correct_words, extra_words, misspelled_words, target_word_count)
    and updates cumulative_hist (word -> count of times user failed that target word).
    """
    target_words = split_words(target_line)
    user_words = split_words(user_line)

    i = 0
    correct = 0
    extra = 0
    misspelled = 0

    max_len = len(target_words)
    user_len = len(user_words)

    while i < max_len or i < user_len:
        if i < max_len and i < user_len:
            if user_words[i] == target_words[i]:
                correct = correct + 1
            else:
                misspelled = misspelled + 1
                update_histogram_word(cumulative_hist, target_words[i])
        elif i < max_len:
            # user missing a word -> counts as misspelled for that target position
            misspelled = misspelled + 1
            update_histogram_word(cumulative_hist, target_words[i])
        else:
            # user wrote extra words beyond target length
            extra = extra + 1
        i += 1

    return correct, extra, misspelled, len(target_words)

def precision_percentage(total_correct, total_extra, total_target_words):
    if total_target_words == 0:
        return 0.0
    value = ((total_correct - total_extra) / float(total_target_words)) * 100.0
    return round(value, 2)

def sort_histogram_items(hist):
    # Sort by count desc, word asc – without lambda
    items = []
    for key in hist:
        items.append((key, hist[key]))

    # selection sort
    sorted_items = []
    while len(items) > 0:
        best_index = 0
        j = 1
        while j < len(items):
            key_best, cnt_best = items[best_index]
            key_j, cnt_j = items[j]
            better = False
            if cnt_j > cnt_best:
                better = True
            elif cnt_j == cnt_best and key_j < key_best:
                better = True
            if better:
                best_index = j
            j += 1
        sorted_items.append(items[best_index])
        del items[best_index]
    return sorted_items

def print_histogram(hist):
    sorted_items = sort_histogram_items(hist)
    for item in sorted_items:
        word = item[0]
        count = item[1]
        hashes = ""
        k = 0
        while k < count:
            hashes = hashes + "#"
            k += 1
        label = word
        spaces_needed = 21 - len(label)
        if spaces_needed < 0:
            spaces_needed = 0
        spaces = ""
        s = 0
        while s < spaces_needed:
            spaces = spaces + " "
            s += 1
        print(label + spaces + ": " + hashes)

def round_minutes(total_seconds):
    if total_seconds < 60.0:
        return 1
    minutes = int(total_seconds // 60)
    seconds_left = total_seconds - (minutes * 60)
    if seconds_left >= 30.0:
        minutes = minutes + 1
    return minutes

def compute_wpm_and_accuracy(total_typed_words, misspelled_words, extra_words, total_seconds):
    minutes = round_minutes(total_seconds)
    if minutes <= 0:
        minutes = 1

    gross = total_typed_words / float(minutes)
    penalty = (misspelled_words + extra_words) / float(minutes)
    net = gross - penalty
    if net < 0:
        net = 0.0

    acc = 0.0
    if gross > 0.0:
        acc = (net / gross) * 100.0

    return round(gross, 2), round(net, 2), round(acc, 2), minutes

def animal_for_net_wpm(net_wpm):
    i = 0
    while i < len(ANIMAL_THRESHOLDS):
        low, high, eng, swe = ANIMAL_THRESHOLDS[i]
        if net_wpm >= low and net_wpm <= high:
            return eng, swe
        i += 1
    return "", ""

def safe_read_scores(scores_path):
    if not os.path.isfile(scores_path):
        return []
    rows = []
    f = None
    try:
        f = open(scores_path, "r", encoding="utf-8")
        for raw in f:
            line = raw.strip()
            if line == "":
                continue
            # Expect format: name\tprecision\tdifficulty
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            name = parts[0]
            try:
                prec = float(parts[1])
            except Exception:
                continue
            diff = parts[2]
            rows.append((name, prec, diff))
    finally:
        if f is not None:
            f.close()
    return rows

def print_scores_grouped(scores_path):
    rows = safe_read_scores(scores_path)
    if len(rows) == 0:
        print("No scores saved yet.")
        return

    # Group by difficulty
    difficulties = ("easy", "medium", "hard")
    d_index = 0
    while d_index < len(difficulties):
        diff = difficulties[d_index]
        group = []
        i = 0
        while i < len(rows):
            if rows[i][2] == diff:
                group.append(rows[i])
            i += 1

        # Sort group by precision desc then name asc (selection sort)
        sorted_group = []
        while len(group) > 0:
            best = 0
            j = 1
            while j < len(group):
                name_b, prec_b, _ = group[best]
                name_j, prec_j, _ = group[j]
                better = False
                if prec_j > prec_b:
                    better = True
                elif prec_j == prec_b and name_j < name_b:
                    better = True
                if better:
                    best = j
                j += 1
            sorted_group.append(group[best])
            del group[best]

        # Print lines like example
        k = 0
        while k < len(sorted_group):
            name, prec, diff_str = sorted_group[k]
            name_col = name
            spaces1 = ""
            j = 0
            while j < (8 - len(name_col) if 8 - len(name_col) > 1 else 1):
                spaces1 = spaces1 + " "
                j += 1
            prec_str = str(round(prec, 2))
            spaces2 = ""
            j = 0
            while j < (10 - len(prec_str) if 10 - len(prec_str) > 1 else 1):
                spaces2 = spaces2 + " "
                j += 1
            print(name_col + spaces1 + prec_str + spaces2 + diff_str)
            k += 1

        d_index += 1

def append_score(scores_path, name, precision, difficulty):
    f = None
    try:
        f = open(scores_path, "a", encoding="utf-8")
        line = name + "\t" + str(round(precision, 2)) + "\t" + difficulty + "\n"
        f.write(line)
    finally:
        if f is not None:
            f.close()

def run_test(file_path, difficulty, scores_filename):
    lines = read_lines(file_path)
    hist = {}

    total_correct = 0
    total_extra = 0
    total_misspelled = 0
    total_target_words = 0
    total_typed_words = 0

    start_time = time.time()

    idx = 0
    while idx < len(lines):
        target = lines[idx]
        print("Skriv in:", target)
        user = input(">>> ")

        correct, extra, misspelled, target_count = compute_line_stats(target, user, hist)

        # Update totals
        total_correct = total_correct + correct
        total_extra = total_extra + extra
        total_misspelled = total_misspelled + misspelled
        total_target_words = total_target_words + target_count
        # Count all typed words in this line
        typed_words = split_words(user)
        total_typed_words = total_typed_words + len(typed_words)

        # Print current performance (cumulative)
        precision_now = precision_percentage(total_correct, total_extra, total_target_words)
        print("\nOrdprecision:", str(precision_now) + "%")
        if len(hist) > 0:
            print_histogram(hist)
        else:
            print("(Inga fel ännu)")
        print("")
        idx = idx + 1

    end_time = time.time()
    duration_seconds = end_time - start_time

    input("Grattis! Tryck enter för att se resultatet.\n>>> ")

    # Final results
    final_precision = precision_percentage(total_correct, total_extra, total_target_words)
    print("\nOrdprecision:", str(final_precision) + "%")
    if len(hist) > 0:
        print_histogram(hist)

    print(
        "Det tog "
        + str(int(duration_seconds // 60))
        + " minuter och "
        + str(duration_seconds - int(duration_seconds // 60) * 60)
        + " sekunder"
    )

    gross_wpm, net_wpm, acc_pct, _ = compute_wpm_and_accuracy(
        total_typed_words, total_misspelled, total_extra, duration_seconds
    )

    print("Gross WPM:", gross_wpm)
    print("Net WPM:", net_wpm)
    print("Accuracy:", str(acc_pct) + "%")

    eng, swe = animal_for_net_wpm(net_wpm)
    if swe != "":
        print("Du skriver snabbt som en " + swe)
    else:
        print("Hastighetskategori okänd")

    # Save score
    name = input("\nSkriv in ditt namn:\n>>> ").strip()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scores_path = os.path.join(base_dir, scores_filename)
    append_score(scores_path, name, final_precision, difficulty)
    print("Sparat i '" + scores_filename + "'.")
