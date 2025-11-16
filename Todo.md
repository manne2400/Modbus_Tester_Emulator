\## 1. Mål og scope



\*\*Formål:\*\*

En Modbus master/simulator til at:



\* Teste Modbus RTU (RS-485/RS-232) og Modbus TCP/IP forbindelser

\* Læse/skriv coils, discrete inputs, input registers og holding registers

\* Køre flere “vinduer/sessions” parallelt (ligesom Modbus Poll)(\[modbustools.com]\[1])

\* Have god fejlsøgning: hexdump, tidsstempler, log, statuskoder(\[docs.newflow.co.uk]\[2])



\*\*Målgruppe:\*\*

Teknikere/ingeniører der skal:



\* Verificere at et anlæg svarer på Modbus

\* Tjekke adresser og datatyper

\* Skrue midlertidigt på setpoints, bits og parametre



---



\## 2. Overordnede krav



\### 2.1 Protokoller



\* Modbus RTU (master)



&nbsp; \* RS-485/RS-232 via USB-converter

&nbsp; \* Justerbar baudrate, parity, stopbits

\* Modbus TCP (client/master)



&nbsp; \* IP + port (typisk 502)

&nbsp; \* Mulighed for at definere flere forbindelser på én gang(\[thingdash.io]\[3])



(Evt. senere: Modbus UDP, RTU over TCP, Modbus ASCII – men ikke nødvendig i første version.)



\### 2.2 Funktionalitet (minimum)



For hver “session” (et vindue / faneblad):



\* Vælg:



&nbsp; \* Connection profil (RTU eller TCP)

&nbsp; \* Slave ID / Unit ID

&nbsp; \* Function code (01, 02, 03, 04, 05, 06, 15, 16)(\[docs.tia.siemens.cloud]\[4])

&nbsp; \* Startadresse

&nbsp; \* Antal punkter

&nbsp; \* Poll-interval (ms)

\* Vise data i en tabel:



&nbsp; \* Adresse, navn/label, rå værdi, skaleret værdi, status (OK/timeout/exception)

\* Lave skreværdi:



&nbsp; \* Dobbeltklik på cellen og skriv ny værdi (coils, holding registers)(\[modbustools.com]\[5])

\* Start/Stop polling pr. session



\### 2.3 “Nice to have” (som du kan tage i næste version)



\* Navngivne celler (alias/tag navne) og scaling/units(\[modbustools.com]\[1])

\* Real-time trend (graf) af udvalgte registre(\[Scribd]\[6])

\* Data-logging til fil (CSV/JSON)

\* Script-motor (fx sekvenser af læs/skriv, scenarier)



---



\## 3. Arkitektur – lagdeling



Tænk app’en opdelt i lag:



1\. \*\*UI-lag\*\*



&nbsp;  \* Vinduer/faner, tabeller, dialoger til connection og sessions

2\. \*\*Applikations-lag\*\*



&nbsp;  \* Session manager

&nbsp;  \* Polling engine

&nbsp;  \* Tag/skalering og data-model

3\. \*\*Protokol-lag (Modbus)\*\*



&nbsp;  \* Opbygger og parser Modbus-rammer (PDU/ADU)

&nbsp;  \* Håndterer function codes og exceptions(\[ni.com]\[7])

4\. \*\*Transport-lag\*\*



&nbsp;  \* TCP klient

&nbsp;  \* Serial port (RTU)

5\. \*\*Lagring\*\*



&nbsp;  \* Profiler, sessions og tag-lister (fx i JSON eller SQLite)



Hvis du vælger fx Electron+React (som du allerede bruger), svarer det til:



\* UI: React

\* Applikationslag: TypeScript services (session manager osv.)

\* Transport/Modbus: Node-moduler til TCP og seriel + Modbus-bibliotek

\* Lagring: lokal fil/SQLite



(Det samme princip gælder hvis du hellere vil bruge .NET, Python/Qt osv.)



---



\## 4. Datamodeller (konceptuelt)



Ingen kode – kun hvilke “ting” du bør have:



1\. \*\*ConnectionProfile\*\*



&nbsp;  \* Navn

&nbsp;  \* Type: RTU eller TCP

&nbsp;  \* For TCP: host, port, timeout, max retries

&nbsp;  \* For RTU: COM-port, baud, parity, stopbits, data bits, timeout, retries



2\. \*\*SessionDefinition\*\*



&nbsp;  \* Navn

&nbsp;  \* Reference til ConnectionProfile

&nbsp;  \* Slave ID

&nbsp;  \* Function code

&nbsp;  \* Startadresse

&nbsp;  \* Antal punkter

&nbsp;  \* Poll-interval

&nbsp;  \* Liste over Tags (se nedenfor)

&nbsp;  \* Status (Stopped/Running/Error)



3\. \*\*TagDefinition (valgfrit i første version)\*\*



&nbsp;  \* Adressetype (coil, input, holding register, input register)

&nbsp;  \* Adresse (offset)

&nbsp;  \* Navn

&nbsp;  \* Datatype (INT16, UINT16, INT32, FLOAT32, BOOL, osv.)

&nbsp;  \* Byte/word-order (endianness)

&nbsp;  \* Skalering (factor, offset)

&nbsp;  \* Enhed (°C, bar, %, osv.)



4\. \*\*PollResult\*\*



&nbsp;  \* Timestamp

&nbsp;  \* Session ID

&nbsp;  \* Rå data (liste af bytes eller rå værdier)

&nbsp;  \* Dekodede værdier

&nbsp;  \* Fejlkode/status



5\. \*\*LogEntry\*\*



&nbsp;  \* Timestamp

&nbsp;  \* Retning (TX/RX)

&nbsp;  \* Hex-streng

&nbsp;  \* Eventuel fejlbeskrivelse(\[docs.newflow.co.uk]\[2])



---



\## 5. UI-design – hvordan skal app’en se ud?



\### 5.1 Hovedvindue



\* Menu eller toolbar:



&nbsp; \* File: Åbn/Gem konfiguration

&nbsp; \* Connection: Ny/Rediger/Slet connection profile

&nbsp; \* Session: Ny/Stop alle/Start alle

&nbsp; \* View: Vis/Skjul logvindue, hexdump, graf

\* Venstre side: Liste/tree med



&nbsp; \* Connection profiles

&nbsp; \* Under hver: aktive sessions

\* Højre side: Faner (tabs) – én pr. session



&nbsp; \* Øverst: session-bar:



&nbsp;   \* Connection dropdown

&nbsp;   \* Slave ID

&nbsp;   \* Function code

&nbsp;   \* Startadresse, antal

&nbsp;   \* Poll-interval

&nbsp;   \* Start/Stop knap

&nbsp; \* Midt: datatabel

&nbsp; \* Nederst: statuslinje (seneste fejl, svar-tid, antal fejl)



\### 5.2 Connection-dialog



\* Fane for \*\*Modbus TCP\*\*:



&nbsp; \* Navn

&nbsp; \* Host/IP

&nbsp; \* Port

&nbsp; \* Timeout

&nbsp; \* Retries

\* Fane for \*\*Modbus RTU\*\*:



&nbsp; \* Navn

&nbsp; \* Port (liste over fundne COM-porte)

&nbsp; \* Baudrate

&nbsp; \* Parity (None/Even/Odd)

&nbsp; \* Data bits, stop bits

&nbsp; \* Timeout

&nbsp; \* Retries(\[modbustools.com]\[1])



\### 5.3 Log- og debug-vindue



Separat panel eller faneblad med:



\* Liste med TX/RX-linjer med timestamp og hexdump

\* Filtrering (kun TX, kun RX, kun errors)

\* Mulighed for at gemme log til fil(\[docs.newflow.co.uk]\[2])



---



\## 6. Transport-lag (TCP + RTU)



\### 6.1 Modbus TCP klient



\* Åbn TCP-forbindelse til host/port

\* Håndtér:



&nbsp; \* Reconnect ved fejl

&nbsp; \* Timeout på svar

&nbsp; \* Transaction ID / sequence (til at matche svar med forespørgsel)(\[RT-Labs | Industrial communication]\[8])

\* Simpel kø:



&nbsp; \* Én aktiv request ad gangen pr. connection

&nbsp; \* Polling engine sender kun ny request når den forrige er afsluttet eller timed-out



\### 6.2 Modbus RTU (seriel)



\* Åbn seriel port med de valgte parametre

\* Håndtér:



&nbsp; \* Framing baseret på timeouts (stilleperiode = ramme slut)(\[Wikipedia]\[9])

&nbsp; \* CRC16 (Modbus-varianten) – brug bibliotek hvis muligt

\* Hav én “RTU master” pr. bus:



&nbsp; \* Polling engine skal sende forespørgsler efter hinanden (ingen overlap)



---



\## 7. Protokol-lag (Modbus PDU/ADU)



Du skal understøtte mindst:



\* 0x01 – Read Coils

\* 0x02 – Read Discrete Inputs

\* 0x03 – Read Holding Registers

\* 0x04 – Read Input Registers

\* 0x05 – Write Single Coil

\* 0x06 – Write Single Register

\* 0x0F – Write Multiple Coils

\* 0x10 – Write Multiple Registers(\[docs.tia.siemens.cloud]\[4])



Protokol-laget skal kunne:



\* Bygge en request ud fra:



&nbsp; \* Slave ID

&nbsp; \* Function code

&nbsp; \* Startadresse

&nbsp; \* Antal punkter

&nbsp; \* Evt. værdier (ved write)

\* Parse response:



&nbsp; \* Kontrollér fejlkode (funktion + 0x80 = exception)

&nbsp; \* Udpak coil-bits eller register-værdier

\* Give besked til applikations-laget:



&nbsp; \* Om det var OK, timeout, CRC-fejl, protokol-fejl, exception code osv.(\[ni.com]\[7])



---



\## 8. Polling engine og session-logik



\### 8.1 Polling for én session



For hver session:



\* Holder sin egen:



&nbsp; \* Poll-interval

&nbsp; \* Næste poll-tidspunkt

&nbsp; \* Status (Running/Stopped/Error)

\* Loop:



&nbsp; \* Hvis session er Running, og det er tid:



&nbsp;   \* Byg request (via protokol-lag)

&nbsp;   \* Send via connection (transport-lag)

&nbsp;   \* Vent på svar eller timeout

&nbsp;   \* Parse svar

&nbsp;   \* Opdater datatabel

&nbsp;   \* Log TX/RX

&nbsp;   \* Næste poll-tid = nu + interval



\### 8.2 Flere sessions



\* Du kan have:



&nbsp; \* Én poll-timer for hele app’en, der hver X ms kigger på alle sessions

&nbsp; \* Eller én separat timer pr. session

\* Regler:



&nbsp; \* På RTU må kun én request ad gangen per fysisk bus

&nbsp; \* På TCP kan du have flere connections (fx én per device) – stadig typisk én request ad gangen pr. connection for enkelhed(\[thingdash.io]\[3])



---



\## 9. Datatyper, skalering og visning



\### 9.1 Datatyper fra holding/input registers



Standard Modbus register er 16-bit. Men du vil ofte fortolke som:



\* INT16, UINT16

\* INT32, UINT32 (2 registers)

\* FLOAT32 (2 registers)

\* BOOL (bit i coil eller register)



Ting du skal have som konfigurationsmuligheder pr. tag:



\* Datatype (INT16, UINT16, INT32, FLOAT32 osv.)

\* Byte/word-order (Big-endian, Little-endian, swapped)(\[RT-Labs | Industrial communication]\[8])

\* Skalering:



&nbsp; \* Skaleret værdi = rå værdi \* faktor + offset

\* Enhed (string, kun til visning)



\### 9.2 Visning i UI



I tabellen:



\* Kolonner:



&nbsp; \* Adresse (fx 40001 + offset)

&nbsp; \* Navn (fx “Temp fremløb”)

&nbsp; \* Rå værdi

&nbsp; \* Skaleret værdi

&nbsp; \* Enhed

&nbsp; \* Status (OK, Timeout, Error, Exception code)



---



\## 10. Diagnostik-funktioner



For fejlsøgning er det guld værd med:



1\. \*\*Hex-view af telegrammer\*\*



&nbsp;  \* Hver TX/RX linje:



&nbsp;    \* Timestamp

&nbsp;    \* Retning (TX/RX)

&nbsp;    \* Hex streng

&nbsp;    \* Kort kommentar (fx “Read Holding 40001 len=10”)(\[docs.newflow.co.uk]\[2])



2\. \*\*One-shot request\*\*



&nbsp;  \* En lille dialog hvor du manuelt kan:



&nbsp;    \* Vælge function, adresse, antal

&nbsp;    \* Trykke “Send én gang” uden at starte polling



3\. \*\*Manuel write\*\*



&nbsp;  \* Skriv én coil eller ét register uden at det bliver ved med at polle



4\. \*\*Fejloversigt\*\*



&nbsp;  \* Counts:



&nbsp;    \* Antal timeouts

&nbsp;    \* Antal CRC-fejl

&nbsp;    \* Antal Modbus exceptions (per slave og function)



---



\## 11. Lagring af profiler og sessions



Design en simpel struktur, fx:



\* “Connections” fil / tabel



&nbsp; \* Alle ConnectionProfiles

\* “Sessions” fil / tabel



&nbsp; \* Alle SessionDefinitions og tilknyttede Tags



Behov:



\* Import/Export:



&nbsp; \* Eksporter konfiguration til fil (så du kan dele med kollegaer)

\* Seneste projekt:



&nbsp; \* Gem “sidst åbne projekt” og genåbn det automatisk



---



\## 12. Testplan



Når du begynder at bygge, så planlæg test fra start.



\### 12.1 Lab-opsætning



\* \*\*Modbus simulator\*\* (software):



&nbsp; \* Fx en Modbus slave simulator til PC, eller et eksisterende PLC/RTU med kendt map(\[Maisvch Technology]\[10])

\* \*\*Rigtigt udstyr\*\*:



&nbsp; \* En controller eller frekvensomformer du kender adresserne til

&nbsp; \* Både over RTU og TCP, hvis muligt



\### 12.2 Testtyper



1\. \*\*Enhedstest (mentalt / manuelt)\*\*



&nbsp;  \* Tjek at Modbus-requests og -responses ser korrekte ud i hex-loggen i forhold til dokumentation(\[Wikipedia]\[9])



2\. \*\*Funktions-test\*\*



&nbsp;  \* Læs coils/registers fra kendte adresser og sammenlign med anden kendt Modbus-tool

&nbsp;  \* Skriv værdier og verificér at udstyr ændrer sig



3\. \*\*Fejlscenarier\*\*



&nbsp;  \* Kobl kabel fra → forvent timeouts og fejlstatus i UI

&nbsp;  \* Indtast forkert slave ID → se Modbus timeout

&nbsp;  \* Forkert function → se exception codes



4\. \*\*Performance\*\*



&nbsp;  \* Sæt poll-rate ned (hurtigere) og se hvornår udstyr eller din app begynder at fejle

&nbsp;  \* Flere sessions samtidig (fx 5–10) og se CPU/ram og stabilitet(\[docs.newflow.co.uk]\[2])



---



\## 13. Mulige avancerede features (version 2+)



Når grundkernen virker, kan du overveje:



\* Real-time trend charts pr. session

\* En lille “wizard”:



&nbsp; \* Scan gennem adresser og find hvor der kommer non-zero data

\* Script engine:



&nbsp; \* Små sekvenser (fx “sæt coil, vent, læs register, log resultat”)

\* Automatisk “device template”:



&nbsp; \* Import af Excel/CSV med mapping for bestemte fabrikater

\* Sikkerhed:



&nbsp; \* Hvis du senere vil teste over WAN/VPN, kan du overveje TLS, brugernavn/kode osv. på gateway-niveau



---



\[1]: https://www.modbustools.com/mbpoll-user-manual.html?utm\_source=chatgpt.com "Modbus Poll User Manual"

\[2]: https://docs.newflow.co.uk/nano/software/Modbus\_Master\_Simulator\_User\_Manual\_R5.pdf?utm\_source=chatgpt.com "Modbus Master Simulator User Manual - Newflow Ltd"

\[3]: https://www.thingdash.io/blog/modbus-tcp-vs-modbus-rtu-a-practical-comparison?utm\_source=chatgpt.com "Modbus TCP vs Modbus RTU: A Practical Comparison"

\[4]: https://docs.tia.siemens.cloud/r/simatic\_s7\_1200\_manual\_collection\_enus\_20/communication-processor-and-modbus-tcp/modbus-communication/overview-of-modbus-tcp-and-modbus-rtu-communication?utm\_source=chatgpt.com "Overview of Modbus TCP and Modbus RTU communication"

\[5]: https://www.modbustools.com/modbus\_poll.html?utm\_source=chatgpt.com "Modbus Poll"

\[6]: https://www.scribd.com/document/889020713/Modbus-Poll-User-Manual?utm\_source=chatgpt.com "Modbus Poll User Manual | PDF | Microsoft Excel"

\[7]: https://www.ni.com/en/shop/seamlessly-connect-to-third-party-devices-and-supervisory-system/the-modbus-protocol-in-depth.html?srsltid=AfmBOoq2ZS7eN1fIf7j-AFTJrwrzlMJfjDkeYY1rG8Vyi1fA3Weka\_lq\&utm\_source=chatgpt.com "What is the Modbus Protocol \& How Does It Work?"

\[8]: https://rt-labs.com/modbus/modbus-tcp-a-classic-technology-for-modern-solutions/?utm\_source=chatgpt.com "Modbus TCP - A Classic Technology for Modern Applications"

\[9]: https://en.wikipedia.org/wiki/Modbus?utm\_source=chatgpt.com "Modbus"

\[10]: https://maisvch.com/blog/how-to-test-modbus-rs485-a-comprehensive-guide/?utm\_source=chatgpt.com "How to Test Modbus RS485: A Comprehensive Guide"



