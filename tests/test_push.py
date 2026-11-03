from saathi.push import MAX_SMS, to_sms

HEAD = "शान्त: आगामी ७ दिन नदी बाढीको सम्भावना छैन"


def test_blank_line_paragraphs_pack_into_three():
    advice = HEAD + "\n\nSMS 1/3:\nआजको सुझाव: नदी सामान्य छ।\n\nआजको काम: झोला, फोन।\n\nDHM को चेतावनी पालन गर्नुहोस्।"
    msgs = to_sms(advice)
    assert 1 <= len(msgs) <= MAX_SMS
    assert msgs[0].startswith(HEAD)
    assert "SMS 1/3" not in "".join(msgs)


def test_single_newline_wall_of_text_is_still_split():
    # Nova often separates its messages with single newlines; one 600-char text must not go out as one SMS.
    sentence = "नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ। "
    advice = HEAD + "\n\n" + sentence * 4 + "\n " + sentence * 3 + "\n " + sentence * 3
    msgs = to_sms(advice, limit=300)
    assert len(msgs) == MAX_SMS
    assert all(len(m) <= 300 for m in msgs)
    assert msgs[0].startswith(HEAD)


def test_headline_alone_is_one_message():
    assert to_sms(HEAD) == [HEAD]


def test_inline_sms_labels_are_stripped():
    advice = HEAD + "\nSMS 1/3: नदी सामान्य छ।\nSMS 2/3: झोला तयार राख्नुहोस्।"
    msgs = to_sms(advice)
    assert "SMS" not in "".join(msgs)
    assert "नदी सामान्य छ।" in "".join(msgs)
