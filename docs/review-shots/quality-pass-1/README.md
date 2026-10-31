# Quality pass 1

Data-only fixes, no new ideas:

- **Hierarchy sources re-read.** The 7 pages behind the original hierarchy scores (Republic_(Plato), Natural_slavery, Great_chain_of_being, Classless_society, Master–slave_morality, Dark_Enlightenment, Julius_Evola) back their rationales. Three wording fixes: Thomism (degrees of perfection), Traditionalism (Guénon vs Evola split), and Will to power gains the Friedrich_Nietzsche page, which carries the "order of rank" phrase.
- **Dates in US order.** 28 origin notes, 1 edge note and 1 current now read "October 31, 1517" instead of "31 October 1517", with the comma after the year mid-sentence.
- **Years and places checked.** Legalism moves from -233 (Han Fei's death) to c. -359 (Shang Yang's reforms in Qin, which the Legalism page calls the pivotal advance). Advaita Vedanta moves from 788 to c. 700 (Adi_Shankara page: early 8th century; Nakamura 700–750; 788–820 is one monastic tradition). Upanishads place is now the Kuru-Panchala region, and Madhyamaka is the Andhra region. All four keep null coordinates because the sources name a region, not a city.
- **Thin justifications.** 16 hierarchy rationales that ended in "judgment" now state a checkable fact from the idea's own Grokipedia source. No scores changed.
- **Thinker links.** 174 more names are linked in thinkers.json (478 total). Every page returned 200, and its lead was checked against the idea. Alex Williams stays unlinked because the Grokipedia page is about an actor.
- impact.json regenerated (6 values move by 0.1).

`t_qp1.py` serves the `../snip-share` page copy on port 8881 and routes every data file to this branch. Results: `__views.check()` found 0 violations in all 9 views, `__tours.validate()` found 0 bad edges (and the negative control was caught), and panels are OK on desktop and phone for the 7 touched ideas, with 0 console errors.
