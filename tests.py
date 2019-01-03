import unittest
from features import Ida, Volta, Remover, Start, Caronas
from messages import MSGS
from db import DbClient


class DummyDb(DbClient):
    IDA = "10:00 - @usr1\n10:00 - @usr3\n10:00 - @usr2\n"
    VOLTA = "10:00 - @usr1\n10:00 - @usr3\n10:00 - @usr2\n"

    def insere_bd(self, carona):
        pass

    def busca_bd(self, tipo, chat_id):
        return self.IDA if tipo == 1 else self.VOLTA

    def desativar_bd(self, tipo, chat_id, username):
        pass

    def desconectar(self):
        pass


class TestFeatures(unittest.TestCase):

    def test_start(self):
        self.assertEqual(
            Start(None).processar(None, None, None), MSGS["start"])

    def test_caronas(self):
        ida = DummyDb.IDA
        volta = DummyDb.VOLTA
        self.assertEqual(
            Caronas(DummyDb(None)).processar(None, None, None),
            MSGS["ida_titulo"] + str(ida) + MSGS["volta_titulo"] + str(volta)
            )

    def test_remover(self):
        error_msg = MSGS["remove_err"]
        ida_success_msg = str.format(MSGS["removed"], "ida")
        volta_success_msg = str.format(MSGS["removed"], "volta")
        remover = Remover(DummyDb(None))
        self.assertEqual(
            remover.processar("username", None, ["ida"]), ida_success_msg)
        self.assertEqual(
            remover.processar("username", None, ["volta"]), volta_success_msg)
        self.assertEqual(
            remover.processar("username", None, ["wrong"]), error_msg)

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()
