using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GuidMaker
{
    class Program
    {
        static void Main(string[] args)
        {
            int gweeds = 0;

            if (args.Length == 0)
            {
                Console.WriteLine("How many gweeds would you like?");

                try
                {
                    gweeds = int.Parse(Console.ReadLine());
                }
                catch
                {
                    Console.WriteLine("Not an int, go away.");
                    return;
                }
            }
            else
            {
                try
                {
                    gweeds = int.Parse(args[0]);
                }
                catch
                {
                    Console.WriteLine("Not an int, go away.");
                    return;
                }
            }


            for (int i = 0; i < gweeds; i++)
            {
                Console.WriteLine(System.Guid.NewGuid());
            }

            Console.WriteLine("Press the any key to exit.");
            Console.ReadKey();
        }
    }
}
