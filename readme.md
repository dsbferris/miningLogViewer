rigname

total found shares
total amount of logs
total runtime

avg wattage
avg shares/h or day

absolute power used
27,35ct bis 31.03.21
ab 01.04.21 29,8ct

stromkosten je monat


timestamp
hashrate
gpu power, temp
share found (accepted/rejected), ms (ping) until result, nonce

<br/>

###56.586 MH/s werden für 4 sec angenommen
###von hier die shares auswerten ???

2021-02-13 14:12:14: [Statistics] Ethereum - Total speed: 56.586 MH/s, Total shares: 0 Rejected: 0, Time: 00:32

2021-02-13 14:12:18: [Statistics] Ethereum - Total speed: 56.610 MH/s, Total shares: 0 Rejected: 0, Time: 00:36

<br/>

## power und temp werden für diesen zeitraum angenommen

2021-02-13 14:12:11: [Statistics] GPU0 t=57°C fan 30% power 162.56W. Total power: 162.56W

2021-02-13 14:12:18: [Statistics] GPU0 t=59°C fan 30% power 164.17W. Total power: 164.17W

<br/>

## Beispiel einer found share

2021-02-13 14:20:30: <info>  Ethereum - SHARE FOUND (GPU: 0, nonce: 0x6e5f1168b4f12318).

2021-02-13 14:20:30: <info> Ethereum: share denied: Provided PoW solution is invalid! (74 ms).

<br/>

### Es können auch andere Nachrichten zwischengeschoben werden

2021-02-13 14:32:05: <info>  Ethereum - SHARE FOUND (GPU: 0, nonce: 0x63ab933a748c0eab)

2021-02-13 14:32:05: <info>  New job from eth-eu1.nanopool.org:9433

2021-02-13 14:32:05: [Statistics] Ethereum - Total speed: 59.687 MH/s, Total shares: 0 Rejected: 0, Time: 02:10

2021-02-13 14:32:05: [Statistics] Ethereum last 10 min - Total: 60.365 MH/s.

2021-02-13 14:32:05: <info> Ethereum: share denied: Provided PoW solution is invalid! (75 ms).

<br/>

2021-02-13 14:57:13: <info>  Ethereum - SHARE FOUND (GPU: 0, nonce: 0x4ec2e7000db48d64).

2021-02-13 14:57:13: <info> Ethereum: share accepted (22 ms)!

<br/>

##  Achtung vor sonderfällen, die die Statistik verfälschen

2021-02-13 18:07:15: [Statistics] Ethereum - Total speed: inf GH/s, Total shares: 52 Rejected: 0, Time: 03:11:42

2021-02-13 18:07:15: [Statistics] Ethereum last 10 min - Total: -631009104548.975 H/s.

2021-02-13 18:07:17: <info>  New job from eth-eu2.nanopool.org:9433

2021-02-13 18:07:17: [Statistics] Ethereum - Total speed: inf GH/s, Total shares: 52 Rejected: 0, Time: 03:11:44
``