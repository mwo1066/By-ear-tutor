# The order the course teaches in

Generated from `pick_next_index`, the real sequencer — not from file order.
File order is only the starting list; the sequencer spaces categories, honours
`after` anchors, and makes an item wait for the words it is made of.

**213 items.** `word` = an atom, `SENTENCE` = a construction,
`rule` = a feature. A rule shows its nature and tier; a strand has no tier
because it never finishes and so holds no position in a sequence.

The **waits on** column is what actually gates the item: it cannot be taught
until every one of those is.

---

**1.** `tôi` — *I or me*  
    word · waits on —

**2.** `anh` — *address for an older male*  
    word · waits on —

**3.** `xưng hô thay đổi theo người đối diện` — *Vietnamese swaps the word for 'I' depending on who you are talking to — you will meet those soon, and tôi is always safe in the meantime*  
    rule · strand · waits on `tôi`, `anh`

**4.** `tên` — *name*  
    word · waits on —

**5.** `là` — *to be*  
    word · waits on —

**6.** `tôi tên là + [tên riêng]` — *My name is ___*  
    SENTENCE · waits on `tôi`, `tên`, `là`

**7.** `chị` — *address for an older female*  
    word · waits on —

**8.** `em` — *address for a younger person*  
    word · waits on —

**9.** `cách chọn từ xưng hô` — *you have been saying tôi for I, and Vietnamese people hardly ever say it in real life; which word you use depends on who is in front of you, so with Minh — the Vietnamese voice, a man older than you — you are em and he is anh, while your tutor is a woman and would never be anh; keep tôi for strangers, for formal moments, and whenever you are not sure*  
    rule · strand · waits on `anh`, `chị`, `em`

**10.** `bạn` — *you*  
    word · waits on —

**11.** `gì` — *what*  
    word · waits on —

**12.** `bạn tên là gì?` — *What is your name?*  
    SENTENCE · waits on `bạn`, `tên`, `là`, `gì`

**13.** `chào` — *hello*  
    word · waits on —

**14.** `cà phê` — *coffee*  
    word · waits on —

**15.** `nước` — *water*  
    word · waits on —

**16.** `không có giống, không có mạo từ` — *no genders, and no word for 'a' or 'the'*  
    rule · discrete · tier 3 · waits on `cà phê`, `nước`

**17.** `cảm ơn` — *thank you*  
    word · waits on —

**18.** `không` — *no / not*  
    word · waits on —

**19.** `không phải là + [danh từ]` — *I am not a ___*  
    SENTENCE · waits on `không`, `là`

**20.** `muốn` — *to want*  
    word · waits on —

**21.** `từ để hỏi đứng nguyên chỗ` — *a question word like gì stays exactly where the answer would go, so nothing moves in the sentence*  
    rule · discrete · tier 3 · waits on `gì`, `tên`

**22.** `ăn` — *to eat*  
    word · waits on —

**23.** `phủ định: không + [động từ hoặc tính từ]` — *không in front of the action negates it, and in front of a describing word too — one word for both, where English has to switch between don't and am not*  
    rule · discrete · tier 1 · after `không` · waits on `không`, `muốn`, `ăn`

**24.** `uống` — *to drink*  
    word · waits on —

**25.** `đã` — *did, in the past*  
    word · waits on —

**26.** `động từ không chia` — *verbs never change, whoever is doing the action*  
    rule · discrete · tier 1 · after `đã` · waits on `muốn`, `ăn`

**27.** `đã: việc đã xong, đứng trước động từ` — *đã goes right before the action to put it in the past, and you can drop it whenever the time is already clear*  
    rule · discrete · tier 1 · after `động từ không chia` · waits on `đã`, `ăn`

**28.** `rồi` — *already*  
    word · waits on —

**29.** `rồi: việc đã xong` — *rồi on the END of a sentence says it is already done, and it is heard far more often than đã*  
    rule · discrete · tier 2 · after `rồi` · waits on `rồi`, `ăn`

**30.** `chưa` — *not yet*  
    word · waits on —

**31.** `chưa: chưa xong, và cũng để hỏi` — *chưa before the action means not yet; the same chưa on the end turns the sentence into a question*  
    rule · discrete · tier 2 · after `chưa` · waits on `chưa`, `ăn`

**32.** `muốn + [động từ]` — *want ___*  
    SENTENCE · waits on `muốn`

**33.** `cơm` — *rice*  
    word · waits on —

**34.** `có` — *have*  
    word · waits on —

**35.** `câu hỏi có/không` — *có at the front and không at the end wrap any statement into a yes-or-no question — no inversion, no extra verb*  
    rule · discrete · tier 1 · after `có` · waits on `có`, `không`

**36.** `trả lời: lặp lại động từ` — *a yes-or-no question is answered with the verb itself, not with a word for yes — muốn, or không muốn*  
    rule · discrete · tier 1 · after `không` · waits on `có`, `không`, `muốn`

**37.** `câu hỏi có/không: có + [động từ] ... không?` — *do ... not?*  
    SENTENCE · waits on `có`, `không`

**38.** `thích` — *like*  
    word · waits on —

**39.** `và` — *and*  
    word · waits on —

**40.** `này` — *this*  
    word · waits on —

**41.** `các` — *the plural marker*  
    word · waits on —

**42.** `thanh điệu: nghe và bắt chước` — *the same sounds said at a different pitch are different words — so copy the pitch, not just the sounds*  
    rule · strand · waits on `tôi`, `là`

**43.** `ngon` — *delicious*  
    word · waits on —

**44.** `tính từ không cần 'là'` — *in front of a describing word, là disappears: cơm ngon, never cơm là ngon. It only stays in front of a name or a thing, the way you already say tôi tên là Nam*  
    rule · discrete · tier 1 · after `ngon` · waits on `ngon`, `cơm`

**45.** `hiểu` — *to understand*  
    word · waits on —

**46.** `biết` — *to know*  
    word · waits on —

**47.** `nói` — *to speak*  
    word · waits on —

**48.** `ở` — *at, in*  
    word · waits on —

**49.** `người` — *person*  
    word · waits on —

**50.** `danh từ không đổi khi nhiều` — *words don't change in the plural — you add a word instead*  
    rule · discrete · tier 3 · waits on `các`, `người`

**51.** `đâu` — *where*  
    word · waits on —

**52.** `nơi chốn: ở` — *ở marks a PLACE, and it is neither of the other two: English says is for a name, for a description and for a place alike, Vietnamese uses a different word each time*  
    rule · discrete · tier 2 · after `ở` · waits on `ở`, `đâu`

**53.** `bao nhiêu` — *how much*  
    word · waits on —

**54.** `được` — *can, okay*  
    word · waits on —

**55.** `được đứng sau động từ: làm được` — *được means you managed it, and unlike every other helper it goes AFTER the action, not before*  
    rule · discrete · tier 3 · after `được` · waits on `được`, `nói`

**56.** `ai` — *who*  
    word · waits on —

**57.** `rất` — *very*  
    word · waits on —

**58.** `nhưng` — *but*  
    word · waits on —

**59.** `cần` — *to need*  
    word · waits on —

**60.** `cái` — *one, for objects*  
    word · waits on —

**61.** `hai` — *two*  
    word · waits on —

**62.** `con` — *one, for animals*  
    word · waits on —

**63.** `loại từ: số + loại từ + danh từ` — *counting needs a helper between the number and the thing: con for animals, cái for objects, người for people*  
    rule · discrete · tier 2 · waits on `hai`, `cái`, `con`, `người`

**64.** `tiền` — *money*  
    word · waits on —

**65.** `của` — *belonging to*  
    word · waits on —

**66.** `sở hữu: danh từ + của + người` — *của puts the owner LAST — cà phê của tôi, the coffee of me, the reverse of English*  
    rule · discrete · tier 2 · after `của` · waits on `của`, `cà phê`, `tôi`

**67.** `cũng` — *also*  
    word · waits on —

**68.** `cũng đứng trước động từ` — *cũng means also, and it sits right before the action — never at the end the way English puts it*  
    rule · discrete · tier 3 · after `cũng` · waits on `cũng`, `muốn`

**69.** `hơn` — *more than*  
    word · waits on —

**70.** `so sánh: tính từ + hơn` — *hơn after a describing word is how you compare — ngon hơn, better tasting*  
    rule · discrete · tier 3 · after `hơn` · waits on `hơn`, `ngon`

**71.** `lắm` — *a lot, very*  
    word · waits on —

**72.** `rất trước, lắm sau` — *two words for very: rất goes before the describing word, lắm goes after it*  
    rule · discrete · tier 3 · after `rất` · waits on `rất`, `lắm`, `ngon`

**73.** `ạ` — *politely*  
    word · waits on —

**74.** `ạ: một chữ làm câu lịch sự` — *ạ on the end of anything makes it polite — one syllable, no other change, and Vietnamese people notice it at once*  
    rule · discrete · tier 2 · after `ạ` · waits on `ạ`, `cảm ơn`

**75.** `cho` — *to give*  
    word · waits on —

**76.** `hôm nay` — *today*  
    word · waits on —

**77.** `ngày mai` — *tomorrow*  
    word · waits on —

**78.** `hôm qua` — *yesterday*  
    word · waits on —

**79.** `xưng hô đổi theo từng cặp người nói` — *the word you use for 'you' changes with who you're talking to*  
    rule · strand · waits on `anh`, `chị`, `em`

**80.** `sáu` — *six*  
    word · waits on —

**81.** `bảy` — *seven*  
    word · waits on —

**82.** `tám` — *eight*  
    word · waits on —

**83.** `dạ` — *yes, respectfully*  
    word · waits on —

**84.** `lược bỏ chủ ngữ khi đã rõ` — *when it's obvious who you mean, you just drop the word*  
    rule · discrete · tier 3 · waits on `ăn`, `rồi`

**85.** `chín` — *nine*  
    word · waits on —

**86.** `xin` — *please, may I*  
    word · waits on —

**87.** `sao` — *why*  
    word · waits on —

**88.** `thế nào` — *how*  
    word · waits on —

**89.** `tính từ đứng sau danh từ` — *the describing word comes after the thing, not before*  
    rule · discrete · tier 2 · waits on `cà phê`, `ngon`

**90.** `một` — *one*  
    word · waits on —

**91.** `ba` — *three*  
    word · waits on —

**92.** `bốn` — *four*  
    word · waits on —

**93.** `tuổi` — *years old*  
    word · waits on —

**94.** `lịch sự nằm trong từ xưng hô, không phải trong giọng` — *politeness here is not a tone of voice — it is the person-word you pick, plus two small words*  
    rule · strand · waits on `anh`, `chị`, `em`, `dạ`, `ạ`

**95.** `năm` — *five*  
    word · waits on —

**96.** `mười` — *ten*  
    word · waits on —

**97.** `mười một đến mười chín: mười + chữ số` — *for eleven up to nineteen you say mười first and then the digit, in that order and with nothing added*  
    rule · discrete · tier 2 · after `mười` · waits on `mười`

**98.** `mươi` — *ten, in twenty and above*  
    word · waits on —

**99.** `hai mươi trở lên: chữ số + mươi + chữ số` — *from twenty on, the order flips — the digit comes first, then mươi, then the last digit: hai mươi ba is twenty-three*  
    rule · discrete · tier 2 · after `mươi` · waits on `mươi`, `hai`, `ba`

**100.** `mười thành mươi khi có số đứng trước` — *ten on its own is mười, but put a number in front of it and it turns into mươi — one tone mark apart, and two different words*  
    rule · discrete · tier 2 · after `mươi` · waits on `mười`, `mươi`

**101.** `trăm` — *hundred*  
    word · waits on —

**102.** `nghìn` — *thousand*  
    word · waits on —

**103.** `nghìn: chữ số + nghìn` — *thousands stack exactly the same way — a digit and then nghìn, so mười nghìn is ten thousand, which is about what a coffee costs*  
    rule · discrete · tier 1 · after `nghìn` · waits on `nghìn`, `mười`

**104.** `trăm nghìn: tờ tiền hay cầm` — *the notes you actually hold are hundreds of thousands — một trăm nghìn, hai trăm nghìn, năm trăm nghìn*  
    rule · discrete · tier 1 · after `trăm` · waits on `trăm`, `nghìn`, `một`, `hai`, `năm`

**105.** `triệu` — *million*  
    word · waits on —

**106.** `triệu: hàng của tiền thuê và tiền xe` — *above a thousand thousands comes triệu, a million — một triệu, hai triệu, mười triệu*  
    rule · discrete · tier 2 · after `triệu` · waits on `triệu`, `một`, `hai`, `mười`

**107.** `mốt` — *one, as in twenty-one*  
    word · waits on —

**108.** `lăm` — *five, as in twenty-five*  
    word · waits on —

**109.** `năm thành lăm khi đứng cuối` — *năm becomes lăm at the end of a number, because năm also means year and mười năm năm would be unsayable*  
    rule · discrete · tier 3 · after `lăm` · waits on `lăm`, `năm`, `mười`

**110.** `tư` — *four, as in twenty-four*  
    word · waits on —

**111.** `bao nhiêu tiền?` — *how much does it cost?*  
    SENTENCE · waits on `bao nhiêu`, `tiền`

**112.** `số + [đồ uống]: hai cà phê` — *two coffees*  
    SENTENCE · waits on `hai`, `cà phê`

**113.** `Tôi ... tuổi` — *I am twenty years old*  
    SENTENCE · waits on `tôi`, `tuổi`

**114.** `ghép số: chữ số + đơn vị` — *numbers here are built, not memorised — you stack words you already know, so ten digits carry you far past a hundred with nothing new to learn*  
    rule · strand · waits on `mười`, `mươi`

**115.** `ấy` — *that one*  
    word · waits on —

**116.** `nói VỀ ai đó: xưng hô + ấy` — *ấy after a person-word turns speaking TO someone into speaking ABOUT them — anh, then anh ấy*  
    rule · discrete · tier 1 · after `ấy` · waits on `ấy`, `anh`, `chị`

**117.** `ơi` — *hey, when you call someone*  
    word · waits on —

**118.** `gọi ai đó: xưng hô + ơi` — *ơi after a person-word calls out to them — it is how you get a waiter's attention across a room*  
    rule · discrete · tier 1 · after `ơi` · waits on `ơi`, `anh`, `chị`

**119.** `phải` — *must, have to*  
    word · waits on —

**120.** `có thể` — *to be able to*  
    word · waits on `có`

**121.** `nên` — *should*  
    word · waits on —

**122.** `cô` — *aunt*  
    word · waits on —

**123.** `nói giá: chỉ cần con số` — *to say a price you stop at the number — mười nghìn and nothing after it, because the name of the currency is left out and everyone still understands*  
    rule · discrete · tier 1 · waits on `nghìn`

**124.** `chú` — *uncle*  
    word · waits on —

**125.** `ông` — *address for an elderly man*  
    word · waits on —

**126.** `bà` — *address for an elderly woman*  
    word · waits on —

**127.** `đang` — *in the middle of doing*  
    word · waits on —

**128.** `đang: việc đang diễn ra, đứng trước động từ` — *đang before the action means right now, in the middle of it — the same slot đã uses*  
    rule · discrete · tier 2 · after `đang` · waits on `đang`, `ăn`

**129.** `cháu` — *nephew or niece*  
    word · waits on —

**130.** `mình` — *me, softly*  
    word · waits on —

**131.** `mệt` — *tired*  
    word · waits on —

**132.** `đói` — *hungry*  
    word · waits on —

**133.** `đi` — *to go*  
    word · waits on —

**134.** `phải: bắt buộc, đứng trước động từ` — *phải before the action means you have to, and it takes the same slot as muốn and cần*  
    rule · discrete · tier 2 · after `phải` · waits on `phải`, `đi`

**135.** `buồn` — *sad*  
    word · waits on —

**136.** `đẹp` — *beautiful*  
    word · waits on —

**137.** `về` — *to go home, to return*  
    word · waits on —

**138.** `đến` — *to come, to arrive*  
    word · waits on —

**139.** `ra` — *to go out*  
    word · waits on —

**140.** `quả` — *one, for fruit*  
    word · waits on —

**141.** `vào` — *to go in*  
    word · waits on —

**142.** `lên` — *to go up*  
    word · waits on —

**143.** `xuống` — *to go down*  
    word · waits on —

**144.** `chiếc` — *one, for vehicles*  
    word · waits on —

**145.** `ngủ` — *to sleep*  
    word · waits on —

**146.** `làm` — *to do, to work*  
    word · waits on —

**147.** `học` — *to study*  
    word · waits on —

**148.** `ghép hai từ đã biết thành từ mới` — *Vietnamese builds new words by putting two words you already know side by side — đi is to go and học is to study, so đi học is going to school. Use it to work out a word nobody taught you, never to invent one.*  
    rule · strand · waits on `làm`, `ăn`, `uống`

**149.** `chơi` — *to play, to hang out*  
    word · waits on —

**150.** `hỏi` — *to ask*  
    word · waits on —

**151.** `nghe` — *to listen*  
    word · waits on —

**152.** `nhất` — *the most*  
    word · waits on —

**153.** `đọc` — *to read*  
    word · waits on —

**154.** `viết` — *to write*  
    word · waits on —

**155.** `nhớ` — *to remember, to miss*  
    word · waits on —

**156.** `vì` — *because*  
    word · waits on —

**157.** `quên` — *to forget*  
    word · waits on —

**158.** `thấy` — *to see, to feel*  
    word · waits on —

**159.** `gặp` — *to meet*  
    word · waits on —

**160.** `còn` — *and what about*  
    word · waits on —

**161.** `giúp` — *to help*  
    word · waits on —

**162.** `chờ` — *to wait*  
    word · waits on —

**163.** `tìm` — *to look for*  
    word · waits on —

**164.** `nữa` — *more, again*  
    word · waits on —

**165.** `mua` — *to buy*  
    word · waits on —

**166.** `bán` — *to sell*  
    word · waits on —

**167.** `lấy` — *to take*  
    word · waits on —

**168.** `trong` — *inside*  
    word · waits on —

**169.** `đừng` — *don't do it*  
    word · waits on —

**170.** `trên` — *on top of*  
    word · waits on —

**171.** `dưới` — *underneath*  
    word · waits on —

**172.** `với` — *with*  
    word · waits on —

**173.** `xin lỗi` — *sorry*  
    word · waits on `xin`

**174.** `vâng` — *yes, politely*  
    word · waits on —

**175.** `không sao` — *no problem*  
    word · waits on `không`, `sao`

**176.** `sẽ` — *will*  
    word · waits on —

**177.** `sẽ: việc sắp tới, đứng trước động từ` — *sẽ before the action puts it in the future, in the same slot as đã and đang, and it is just as optional*  
    rule · discrete · tier 2 · after `sẽ` · waits on `sẽ`, `ăn`

**178.** `Rất vui được gặp bạn` — *nice to meet you*  
    word · waits on `rất`, `được`, `gặp`, `bạn`

**179.** `Bạn bao nhiêu tuổi?` — *how old are you?*  
    word · waits on `bạn`, `bao nhiêu`, `tuổi`

**180.** `Đến từ` — *come from*  
    word · waits on `đến`

**181.** `Bạn đến từ đâu?` — *where are you from?*  
    word · waits on `bạn`, `Đến từ`, `đâu`

**182.** `Tôi đến từ ...` — *I come from ___*  
    SENTENCE · waits on `tôi`, `Đến từ`

**183.** `Bạn làm gì?` — *what do you do?*  
    word · waits on `bạn`, `làm`, `gì`

**184.** `Xin chào` — *hello (formal)*  
    word · waits on `xin`, `chào`

**185.** `Chào buổi sáng` — *good morning*  
    word · waits on `chào`

**186.** `Chào buổi chiều` — *good afternoon*  
    word · waits on `chào`

**187.** `Tạm biệt` — *goodbye*  
    word · waits on —

**188.** `Chào buổi tối` — *good evening*  
    word · waits on `chào`

**189.** `Hẹn gặp lại` — *see you again*  
    word · waits on `gặp`

**190.** `Bạn có anh chị em không?` — *Do you have siblings?*  
    SENTENCE · waits on `bạn`, `có`, `anh`, `chị`, `em`, `không`

**191.** `Tôi có anh chị em` — *I have siblings*  
    SENTENCE · waits on `tôi`, `có`, `anh`, `chị`, `em`

**192.** `Khỏe` — *healthy*  
    word · waits on —

**193.** `Sống` — *to live*  
    word · waits on —

**194.** `Chào anh / Chào chị / Chào em` — *hello (to male/female/younger)*  
    SENTENCE · waits on `chào`, `anh`, `chị`, `em`

**195.** `Cảm ơn bạn` — *thank you*  
    SENTENCE · waits on `cảm ơn`, `bạn`

**196.** `Không có gì` — *you're welcome*  
    SENTENCE · waits on `không`, `có`, `gì`

**197.** `Tôi tên là [tên], tôi đến từ [nước]` — *My name is Nam and I come from France*  
    SENTENCE · waits on `tôi`, `tên`, `là`, `Đến từ`

**198.** `sân bay` — *airport*  
    word · waits on —

**199.** `khách sạn` — *hotel*  
    word · waits on —

**200.** `Bạn đi đến [địa điểm] không?` — *Where are you going?*  
    SENTENCE · waits on `bạn`, `đi`, `không`

**201.** `nhạc` — *music*  
    word · waits on —

**202.** `đàn guitar` — *guitar*  
    word · waits on —

**203.** `hát` — *to sing*  
    word · waits on —

**204.** `chúc mừng` — *congratulations*  
    word · waits on —

**205.** `Bạn chơi [đàn ...] không?` — *Do you play ...?*  
    SENTENCE · waits on `bạn`, `không`

**206.** `Bạn khỏe không?` — *how are you?*  
    SENTENCE · waits on `bạn`, `Khỏe`, `không`

**207.** `đặt` — *to order*  
    word · waits on —

**208.** `gọi` — *to ask for*  
    word · waits on —

**209.** `Tôi muốn đặt ...` — *I want to order ...*  
    SENTENCE · waits on `tôi`, `muốn`, `đặt`

**210.** `phở` — *pho, the noodle soup*  
    word · waits on —

**211.** `Bạn có thể đặt ... không?` — *Can you order this?*  
    SENTENCE · waits on `bạn`, `có`, `đặt`, `không`

**212.** `Bạn muốn [số lượng] [món] không` — *How many ...?*  
    SENTENCE · waits on `bạn`, `muốn`, `không`

**213.** `đặt [món] được không ạ` — *Is that okay?*  
    SENTENCE · waits on `đặt`, `không`
