using System;
using System.Windows.Forms;
using System.IO;
using Newtonsoft.Json;

namespace KeyboardSoundPlayer
{
    public partial class Form3 : Form
    {
        public Form3()
        {
            InitializeComponent();
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void Form3_Load(object sender, EventArgs e)
        {
            if (!File.Exists("keys.json")) {
                File.Create("keys.json").Close();
                File.WriteAllText("keys.json", "{}");
            }
            dynamic keys = JsonConvert.DeserializeObject(File.ReadAllText("keys.json"));
            string s = "";
            foreach(Newtonsoft.Json.Linq.JProperty entry in keys)
            {
                s += entry.Name.ToUpper() + "     >>     " + entry.Value + "\n\n";
            }
            label1.Text = s;
  
        }

        private void listBox1_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void label2_Click(object sender, EventArgs e)
        {

        }
    }
}
