<h1 align="center">🧾 Wallet Balance Checker</h1>

<p align="center">
  <b>Check Ethereum, Base & BSC wallet balances easily with row control and cancel command.</b><br>
  <i>Choose your range. Cancel anytime. Save progress automatically.</i>
</p>

---

<h2>⚙️ Features</h2>

<ul>
  <li>✅ Supports <b>Ethereum</b>, <b>Base</b>, and <b>BSC</b> networks</li>
  <li>✅ Choose any <b>start</b> and <b>end</b> row</li>
  <li>✅ Type <code>cancel</code> to stop safely</li>
  <li>✅ Auto-saves every 100 results</li>
  <li>✅ File names include range (e.g. <code>balances_50-1000.xlsx</code>)</li>
  <li>✅ Option to restart or exit after stopping</li>
</ul>

---

<h2>📦 Requirements</h2>

<p>Make sure you have <b>Python 3.8+</b> installed.</p>

pip install pandas requests openpyxl
<h2>📁 Input File</h2> <p>Your input file must be named <code>addresses.csv</code> and placed in the same folder as the script.</p> <p>Each line should contain a JSON object with an address:</p>
json

{"address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}
{"address": "0x00000000219ab540356cBB839Cbe05303d7705Fa"}

<h2>🚀 How to Run</h2> <ol> <li>Open terminal in the script directory.</li> <li>Run: <pre><code>python balance_checker.py</code></pre></li> <li>Enter starting row (e.g., <code>50</code>).</li> <li>Enter ending row (or press Enter for all).</li> <li>Watch live progress as balances are fetched.</li> </ol>
<h2>🛑 Cancel Command</h2> <p>At any time, type:</p> <pre><code>cancel</code></pre> <p>The script will safely stop after the current batch and save your progress automatically.</p>
<h2>💾 Output</h2> <p>Results are saved automatically as:</p> <pre><code>balances_50-1000.xlsx</code></pre> <p>Each file includes:</p> <table> <thead> <tr> <th>address</th> <th>Ethereum_ETH</th> <th>Base_ETH</th> <th>BSC_ETH</th> </tr> </thead> <tbody> <tr> <td>0x...</td> <td>0.000000000000000123</td> <td>0.000000000000000000</td> <td>0.000000000000045678</td> </tr> </tbody> </table> <p>All balances are stored with <b>18 decimal precision</b>.</p>
<h2>🔁 Restart or Exit</h2> <p>After completion or cancellation, you’ll see:</p> <pre><code>Do you want to start again? (yes/no)</code></pre> <ul> <li>Type <b>yes</b> to start another range.</li> <li>Type <b>no</b> to exit the program.</li> </ul>
<h2>🧠 Notes</h2> <ul> <li>Safe to re-run for different row ranges.</li> <li>Avoid running multiple instances simultaneously.</li> <li>Progress auto-saves every 100 results.</li> </ul>
<h3 align="center">👨‍💻 Author: Ahmed Sumon</h3> <p align="center"> <b>Version:</b> 2.0<br> <b>License:</b> Free for personal and educational use </p>
