# Memeplex link audit — local copy only (nothing pushed)

Base: merged main ideas.json (142 ideas, from /workspace/yt, = main after PR #26 + #25). Note: /workspace/privacybot/repos/arx-memeplex/ideas.json is the pre-merge 128-idea version, so it was not used.
Result: 145 ideas. validate.py OK (parents exist, no parent later than child); no cycles; all 5 v3 tours still walk real edges.

## New ideas (3)
| id | year/place | parents | source |
|---|---|---|---|
| islam | c. 610, Mecca (Muhammad) | none yet (see decisions) | https://grokipedia.com/page/Islam |
| kalam | c. 720, Basra (Wasil ibn Ata, Mu'tazila) | islam | https://grokipedia.com/page/Kalam |
| mevlevi_order | c. 1273, Konya (Rumi, Sultan Veled) | sufism | https://grokipedia.com/page/Mevlevi_Order |

Islam is NOT a root and no axis was added (proposal below).

## Edges added (10)
- islam → sufism — Sufism is the inward path within Islam. https://grokipedia.com/page/Sufism
- neoplatonism → sufism — **flagged contested** (`edge_notes` field): Grokipedia speaks of shared Neoplatonic heritage, not direct adoption. https://grokipedia.com/page/Sufism
- islam → falsafa — Islamic philosophers worked inside a Muslim setting (falsafa stays the islamic_philosophy root). https://grokipedia.com/page/Islamic_philosophy
- islam → kalam — Kalam is Islamic theology. https://grokipedia.com/page/Kalam
- kalam → asharism — Ash'arism is one of Kalam's main schools (fixes an orphan). https://grokipedia.com/page/Kalam
- sufism → mevlevi_order — a Sufi order founded on Rumi's legacy. https://grokipedia.com/page/Mevlevi_Order
- accelerationism → neoreaction — right-wing accelerationism is described as interwoven with NRx (Nick Land). https://grokipedia.com/page/Accelerationism
- neoplatonism → renaissance_humanism — Ficino translated Plotinus and made Platonic thought central to Renaissance learning. https://grokipedia.com/page/Marsilio_Ficino
- advaita_vedanta → traditionalism and sufism → traditionalism — Guénon built his metaphysics on Vedanta (Man and His Becoming According to the Vedanta, 1925) and took up Sufi practice in Cairo. https://grokipedia.com/page/Ren%C3%A9_Gu%C3%A9non

## Edges removed (1, clearly wrong)
- christianity → old_norse_religion — Norse religion is pre-Christian; Christians only wrote it down later. It is not a descendant. https://grokipedia.com/page/Old_Norse_religion

## Other edits
- sufism: al-Ghazali added to thinkers (his synthesis of Sufism and Sunni theology is noted; not drawn as an edge, since Ash'arism (c. 900) and Sufism (c. 700) both predate him). Platonism rating 0→1 with a "scholars dispute it" rationale. Source added: https://grokipedia.com/page/Al-Ghazali
- New optional field `edge_notes` {parent: {status, src, note}} on sufism. validate.py accepts it; the UI does not show it yet.

## Loose links for ResearchBot (left in place, not cut — per the owner: only clearly wrong edges are removed)
- hermetic_correspondence → romanticism: direct handoff, or only via Renaissance/Böhme? Which Romantics cite Hermetic texts?
- romanticism → wicca: is Gardner's documented source Romanticism, or Margaret Murray/ceremonial magic (Golden Dawn), which aren't on the map?
- mohism ← confucian_ethics: is "Mozi first studied Confucian teaching" (Huainanzi) solid enough?
- shinto ← buddhas_dharma: Shinto isn't descended from Buddhism; is the 712 Kojiki framing (Buddhist/Chinese influence) a real handoff?
- manichaeism: missing Zoroastrian and Buddhist sources (neither on map as such; Buddhism is)? Add buddhas_dharma → manichaeism? **Resolved:** manichaeism now has buddhas_dharma and zoroastrianism parents (ancient Judaism branches PR).
- scientific_racism ← enlightenment_liberalism: what's the documented handoff (Enlightenment classification, e.g. Linnaeus/Blumenbach)?
- populism (1892) ← social_contract: People's Party link to social-contract thought is thin; better parent?
- christian_fundamentalism ← methodism: main sources are Princeton theology and dispensationalism; is Methodism a real parent?
- civil_rights_movement ← christianity: should it be protestantism (Black Baptist churches, King)?
- spinozism has no children: Spinoza → German Idealism / Hegel (pantheism controversy)? Couldn't confirm on Grokipedia's Hegel page.
- renaissance_humanism → protestantism (Erasmus) — missing edge?
- jingjiao → jesuit_accommodation: both ideas are on the map (jesuit_accommodation, 1583), but this edge is not drawn and should stay cut. The stele was unearthed between 1621 and 1625, after Ricci died in 1610, so the Jesuits received it; they did not descend from it (loose-links batch 1).

## Open questions
1. **Islam's parents.** Islam is a monotheistic Abrahamic religion (Grokipedia), but the map has no Judaism idea and a christianity → islam edge would be a claim about descent that Muslims and many historians would frame differently. Options: add second_temple_judaism / rabbinic Judaism and link both, or leave Islam with no parents.
2. **Islam as root (proposal only, not done).** Make islam the root of a new "islam" tradition axis (like christianity), so every idea gets an Islam rating; falsafa would stay the islamic_philosophy root. Cost: one rating + rationale per idea (145×), new validator check. Recommend yes if more Islamic ideas (Shia, Salafism, Islamism, orders) are coming.
3. **second_temple_judaism as Christianity's parent:** needs a new idea (c. 515 BCE, Jerusalem). Christianity is currently a root; a parent would be allowed (roots can have parents) but Judaism would be a natural root too. **Resolved:** second_temple_judaism, hellenistic_judaism and jewish_apocalypticism are now Christianity's parents.
4. **Old Norse religion is now an orphan** (pagan, so it can't be a root). Its date (1270) is the manuscript date. Options: redate to the Viking Age and give it a Proto-Germanic/Indo-European parent (none on map), or leave it parentless.
5. **epicureanism is an orphan** (not a root): add Democritus's atomism (c. 420 BCE) as a new idea, or leave it parentless. **Resolved:** atomism (from the Eleatics) is now epicureanism's parent.
6. More Sufi orders (Qadiriyya, Naqshbandi, Chishti) — only Mevlevi was added.

## Renames: parentheticals dropped from names (28; ids unchanged)
How aliases work: the page (memeplex.html, the `aliasesOf` function used by Memele and Compare search) builds aliases from the name, the id, any text in brackets in the name, and a hard-coded `EXTRA` list. Once the brackets are gone, those bracket aliases disappear, so each idea now has an explicit `aliases` array in ideas.json. **The live page doesn't read `aliases` yet.** It needs a one-line change, prepared locally in `memeplex.aliases-patch.html` (adds `(d.aliases || []).forEach(t => add(t, 0));` to aliasesOf). That change has to ship along with the data, or search and Memele lose those terms.

| id | old name | new name | aliases | added to summary |
|---|---|---|---|---|
| apostolic_christianity | Apostolic Christianity (the shared church before the 1054 split) | Apostolic Christianity | early church, undivided church | (already in summary) |
| oriental_orthodoxy | Oriental Orthodoxy (after 451) | Oriental Orthodoxy | non-Chalcedonian churches | (already in summary) |
| protestantism | Protestantism (Lutheranism) | Protestantism | Lutheranism | Began as Lutheranism. |
| tridentine_catholicism | Counter-Reformation (Tridentine) Catholicism | Counter-Reformation Catholicism | Tridentine, Tridentine Catholicism, Counter-Reformation | Also called Tridentine Catholicism. |
| daoist_way | The Dao (Tao Te Ching) | The Dao | Tao Te Ching, Daoism, Taoism | (already in summary) |
| upanishadic_brahman | Brahman and Atman (Upanishads) | Brahman and Atman | Upanishads | (already in summary) |
| madhyamaka | Madhyamaka (Mahayana emptiness) | Madhyamaka | Mahayana emptiness | Mahayana teaching on emptiness. |
| american_communism | American communism (CPUSA) | American communism | CPUSA, Communist Party USA | Mainly the CPUSA. |
| rationalist_community | Rationalists (LessWrong) | Rationalists | LessWrong | Centered on LessWrong. |
| chan_culture | Chan culture (4chan) | Chan culture | 4chan | (already in summary) |
| effective_accelerationism | Effective accelerationism (e/acc) | Effective accelerationism | e/acc, eacc | Also called e/acc. |
| jingjiao | Jingjiao (Tang-dynasty Christianity) | Jingjiao | Tang-dynasty Christianity | Tang-dynasty Christianity. |
| jesuit_accommodation | Jesuit accommodation in China (Ricci) | Jesuit accommodation in China | Ricci | Led by Matteo Ricci. |
| kokugaku | Kokugaku (National Learning) | Kokugaku | National Learning | Means National Learning. |
| pure_land | Pure Land Buddhism (Jodo-shu) | Pure Land Buddhism | Jodo-shu | Jodo-shu in Japan. |
| vajrayana | Vajrayana (Tantric Buddhism) | Vajrayana | Tantric Buddhism | Also called Tantric Buddhism. |
| modern_druidry | Modern Druidry (Druid revival) | Modern Druidry | Druid revival | (already in summary) |
| rodnovery | Rodnovery (Slavic Native Faith) | Rodnovery | Slavic Native Faith | (already in summary) |
| romuva | Romuva (Baltic faith) | Romuva | Baltic faith | (already in summary) |
| heathenry | Heathenry (Ásatrú) | Heathenry | Ásatrú, Asatru | Also called Asatru. |
| hellenism_revival | Hellenism (modern Greek polytheism) | Hellenism | modern Greek polytheism, Hellenic polytheism | (already in summary) |
| nazism | National Socialism (Nazism) | National Socialism | Nazism, Nazis | Also called Nazism. |
| leninism | Leninism (Bolshevism) | Leninism | Bolshevism, Bolsheviks | Also called Bolshevism. |
| comintern | Comintern (Communist International) | Comintern | Communist International, Third International | (already in summary) |
| social_justice_movement | Social justice (woke) | Social justice | woke, social justice movement | (already in summary) |
| maga | MAGA (Make America Great Again) | MAGA | Make America Great Again | Make America Great Again. |
| kalam | Kalam (Islamic theology) | Kalam | Islamic theology | Islamic theology. |
| mevlevi_order | Mevlevi order (Whirling Dervishes) | Mevlevi order | Whirling Dervishes | (already in summary) |

Re-checked after renames: validate.py OK (145 ideas); no cycles; all 5 tours walk real edges.
