using System;
using System.Windows.Forms;
using System.Diagnostics;
using System.IO;
using Newtonsoft.Json;
using System.Threading;

namespace KeyboardSoundPlayer
{
    public partial class Form2 : Form
    {
        public Form2()
        {
            InitializeComponent();
        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void Form2_Load(object sender, EventArgs e)
        {
            if (!File.Exists("config.json"))
            {
                File.Create("config.json").Close();
                File.WriteAllText("config.json", "{\"gender\": \"male\",\"rate\": 170,\"channels\": 8,\"yt_update\": false,\"exit_key\": \"esc\"}");
            }
            dynamic keys = JsonConvert.DeserializeObject(File.ReadAllText("config.json"));
            textBox4.Text = keys.channels ?? "8";
            textBox1.Text = keys.gender ?? "male";
            textBox3.Text = keys.rate ?? "170";
            textBox2.Text = keys.exit_key ?? "esc";
            textBox5.Text = keys.port ?? "6238";
        }

        private void label2_Click_1(object sender, EventArgs e)
        {

        }

        private void numericUpDown1_ValueChanged(object sender, EventArgs e)
        {
            
        }

        private void label3_Click(object sender, EventArgs e)
        {

        }

        private void label3_Click_1(object sender, EventArgs e)
        {

        }

        private void label5_Click(object sender, EventArgs e)
        {

        }

        private void linkLabel1_LinkClicked(object sender, LinkLabelLinkClickedEventArgs e)
        {
            Process.Start("https://github.com/JGLTechnologies/KeyboardSoundPlayer#configjson");
        }

        private void label4_Click(object sender, EventArgs e)
        {

        }

        private async void button1_Click(object sender, EventArgs e)
        {
            dynamic keys = new Newtonsoft.Json.Linq.JObject();
            int channels;
            int rate;
            int port;
            bool error = false;

            errorProvider1.Clear();

            if (textBox1.Text.ToLower() != "male" && textBox1.Text.ToLower() != "female") {
                errorProvider1.SetError(textBox1, "Gender must be male or female.");
                error = true;
            }

            if (int.TryParse(textBox4.Text, out channels))
            {
                if (channels < 1)
                {
                    errorProvider1.SetError(textBox4, "Channels must be a vaild integer that is greater than 0.");
                    error = true;
                }
            }
            else {
                errorProvider1.SetError(textBox4, "Channels must be a vaild integer that is greater than 0.");
                error = true;
            }

            if (int.TryParse(textBox3.Text, out rate))
            {
                if (rate < 1)
                {
                    errorProvider1.SetError(textBox3, "Rate must be a vaild integer that is greater than 0.");
                    error = true;
                }
            }
            else
            {
                errorProvider1.SetError(textBox3, "Rate must be a vaild integer that is greater than 0.");
                error = true;
            }

            if (int.TryParse(textBox5.Text, out port))
            {
                if (port < 1 || port > 10000)
                {
                    errorProvider1.SetError(textBox5, "Port must be a vaild integer between 0 and 10000.");
                    error = true;
                }
            }
            else
            {
                errorProvider1.SetError(textBox5, "Port must be a vaild integer between 0 and 10000.");
                error = true;
            }

            if (!error)
            {
                errorProvider1.Clear();
            }
            else { return; }

            keys.channels = channels;
            keys.gender = textBox1.Text;
            keys.rate = rate;
            keys.exit_key = textBox2.Text.ToLower();
            keys.port = port;
            if (await Form1.IsOnline()) {
                await Form1.RequestPath("stop");
                Thread.Sleep(1);
                Process process = new Process();
                process.StartInfo.FileName = "main.exe";
                process.Start();
            }
            Form1.port = port;
            if (!File.Exists("config.json"))
            {
                File.Create("config.json").Close();
                File.WriteAllText("config.json", "{\"gender\": \"male\",\"rate\": 170,\"channels\": 8,\"yt_update\": false,\"exit_key\": \"esc\"}");
            }
            File.WriteAllText("config.json", JsonConvert.SerializeObject(keys));
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void numericUpDown2_ValueChanged(object sender, EventArgs e)
        {

        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void button3_Click(object sender, EventArgs e)
        {
            textBox4.Text = "8";
            textBox1.Text = "male";
            textBox3.Text = "170";
            textBox2.Text = "esc";
            textBox5.Text = "6238";
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (!File.Exists("config.json"))
            {
                File.Create("config.json").Close();
                File.WriteAllText("config.json", "{\"gender\": \"male\",\"rate\": 170,\"channels\": 8,\"yt_update\": false,\"exit_key\": \"esc\"}");
            }
            dynamic keys = JsonConvert.DeserializeObject(File.ReadAllText("config.json"));
            textBox4.Text = keys.channels ?? "8";
            textBox1.Text = keys.gender ?? "male";
            textBox3.Text = keys.rate ?? "170";
            textBox2.Text = keys.exit_key ?? "esc";
            textBox5.Text = keys.port ?? "6238";
        }

        private void textBox4_TextChanged(object sender, EventArgs e)
        {

        }

        private void textBox3_TextChanged(object sender, EventArgs e)
        {

        }

        private void textBox5_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
