using System;
using System.Diagnostics;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Net.Http;
using Newtonsoft.Json;
using System.IO;
using System.Threading;

namespace KeyboardSoundPlayer
{
    public partial class Form1 : Form
    {
        public static int port;

        public Form1()
        {
            InitializeComponent();
            if (!File.Exists("config.json"))
            {
                port = 6238;
            }
            else {
                try
                {
                    dynamic keys = JsonConvert.DeserializeObject(File.ReadAllText("config.json"));
                    port = keys.port ?? 6238;
                }
                catch { port = 6238; }
            }
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }

        public static async Task<bool> IsOnline() {

            using (HttpClient c = new HttpClient()) {
                c.Timeout = new System.TimeSpan(0, 0, 0, 0, 100);
                try
                {
                    using (HttpResponseMessage r = await c.GetAsync("http://localhost:" + port))
                    {
                        return true;
                    }
                }

                catch { return false; }
            }
        }

        public static async Task RequestPath(string path)
        {

            using (HttpClient c = new HttpClient())
            {
                c.Timeout = new System.TimeSpan(0, 0, 0, 0, 100);
                try
                {
                    using (HttpResponseMessage r = await c.GetAsync("http://localhost:" + port + "/" + path))
                    {
                        // Do nothing
                    }
                }

                catch { return; }
            }
        }

        private async void button2_Click(object sender, EventArgs e)
        {
            await RequestPath("stop");
            errorProvider1.Clear();
        }
 
  

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void button3_Click(object sender, EventArgs e)
        {
            Form2 f2 = new Form2();
            f2.ShowDialog();
        }

        private async void button1_Click(object sender, EventArgs e)
        {   
            if (!await IsOnline())
            {
                errorProvider1.Clear();
                Process process = new Process();
                process.StartInfo.FileName = "main.exe";
                process.Start();
                Thread.Sleep(1);
            }
            else {
                errorProvider1.SetError(button1, "The sound player is already started.");
            }

        }

        private void button4_Click(object sender, EventArgs e)
        {
            if (textBox1.Text == "" || textBox2.Text == "") {
                return;
            }
            if (!File.Exists("keys.json"))
            {
                File.Create("keys.json").Close();
                File.WriteAllText("keys.json", "{}");
            }
            dynamic keys = JsonConvert.DeserializeObject(File.ReadAllText("keys.json"));
            keys[textBox2.Text.ToLower()] = textBox1.Text;
            File.WriteAllText("keys.json", JsonConvert.SerializeObject(keys));
            textBox1.Text = "";
            textBox2.Text = "";
        }

        private void button5_Click(object sender, EventArgs e)
        {
            Form3 f3 = new Form3();
            f3.ShowDialog();
        }

        private void button6_Click(object sender, EventArgs e)
        {
            if (textBox2.Text == "")
            {
                return;
            }
            if (!File.Exists("keys.json"))
            {
                File.Create("keys.json").Close();
                File.WriteAllText("keys.json", "{}");
            }
            Newtonsoft.Json.Linq.JObject keys = (Newtonsoft.Json.Linq.JObject)JsonConvert.DeserializeObject(File.ReadAllText("keys.json"));
            if (keys.ContainsKey(textBox2.Text.ToLower())) {
                keys.Property(textBox2.Text.ToLower()).Remove();
            }
            File.WriteAllText("keys.json", JsonConvert.SerializeObject(keys));
            try
            {
                File.Delete(textBox2.Text.ToLower() + ".mp3");
            }
            catch { return; }
            textBox2.Text = "";
        }
    }
}
